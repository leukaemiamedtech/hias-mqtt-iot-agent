#!/usr/bin/env python3
""" HIAS iotJumpWay Agent Abstract Class

HIAS IoT Agents process all data coming from entities connected to the HIAS
iotJumpWay brokers.

MIT License

Copyright (c) 2023 Peter Moss Leukaemia MedTech Research CIC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files(the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contributors:
- Adam Milton-Barker

"""

import json
import psutil
import requests
import ssl
import threading

from datetime import datetime
from flask import Response

from modules.helpers import helpers
from modules.hiasbch import hiasbch
from modules.hiascdi import hiascdi
from modules.hiashdi import hiashdi
from modules.mqtt import mqtt

from abc import ABC, abstractmethod


class AbstractAgent(ABC):
    """ Abstract class representing a HIAS iotJumpWay IoT Agent.

    This object represents a HIAS iotJumpWay IoT Agent. HIAS IoT Agents
    process all data coming from entities connected to the HIAS iotJumpWay
    broker using the various machine to machine protocols.
    """

    def __init__(self):
        "Initializes the AbstractAgent object."

        self.hiascdi = None
        self.hiashdi = None
        self.mqtt = None

        self.app_types = [
            "Robotics",
            "Application",
            "Staff"]

        self.ignore_types = [
            "Robotics",
            "HIASCDI",
            "HIASHDI",
            "HIASBCH",
            "Staff"]

        self.helpers = helpers("Agent")
        self.confs = self.helpers.confs
        self.credentials = self.helpers.credentials

        self.helpers.logger.info("Agent initialization complete.")

    def hiascdi_connection(self):
        """Instantiates the HIASCDI Contextual Data Interface connection. """

        self.hiascdi = hiascdi(self.helpers)

        self.helpers.logger.info(
            "HIASCDI Contextual Data Interface connection instantiated.")

    def hiashdi_connection(self):
        """Instantiates the HIASCDI Historical Data Interface connection. """

        self.hiashdi = hiashdi(self.helpers)

        self.helpers.logger.info(
            "HIASHDI Historical Data Interface connection instantiated.")

    def mqtt_connection(self, credentials):
        """Initializes the HIAS MQTT connection. """

        self.mqtt = mqtt(
            self.helpers, "Agent", credentials)
        self.mqtt.configure()
        self.mqtt.start()

        self.helpers.logger.info(
            "HIAS iotJumpWay MQTT Broker connection created.")

    def hiasbch_connection(self):
        """Initializes the HIASBCH connection. """

        self.hiasbch = hiasbch(self.helpers)
        self.hiasbch.start()
        self.hiasbch.w3.geth.personal.unlockAccount(
            self.hiasbch.w3.toChecksumAddress(
                self.credentials["hiasbch"]["un"]),
                self.credentials["hiasbch"]["up"], 0)

        self.helpers.logger.info(
            "HIAS HIASBCH Blockchain connection created.")

    def check_accepts_type(self, headers):
        """ Checks the request Accept types. """

        accepted = headers.getlist('accept')
        accepted = accepted[0].split(",")

        if "Accept" not in headers:
            return False

        for i, ctype in enumerate(accepted):
            if ctype not in self.helpers.confs["acceptTypes"]:
                accepted.pop(i)

        if len(accepted):
            return accepted
        else:
            return False

    def check_content_type(self, headers):
        """ Checks the request Content-Type. """

        content_type = headers["Content-Type"]

        if ("Content-Type" not in headers or content_type not in
                self.helpers.confs["contentTypes"]):
            return False
        return content_type

    def check_body(self, payload, text=False):
        """ Checks the request body is valid. """

        response = False
        message = "valid"

        if text is False:
            try:
                json_object = json.loads(json.dumps(
                    payload.json))
                response = json_object
            except TypeError as e:
                response = False
                message = "invalid"
        else:
            if payload.data == "":
                response = False
                message = "invalid"
            else:
                response = payload.data

        self.helpers.logger.info("Request data " + message)

        return response

    def get_entity_details(self, split_topic):
        """Determines entity type and entity from topic

        Args:
            split_topic (list): List of topic parts

        Returns:
            entity_type: The type of the entity
            entity: The id of the entity

        """

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in self.app_types:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        return entity_type, entity

    def get_attributes(self, entity_type, entity):
        """Gets entity attributes from HIASCDI.

        Args:
            entity_type (str): The HIASCDI Entity type.
            entity (str): The entity id.

        Returns:
            dict: Required entity attributes

        """

        attrs = self.hiascdi.get_attributes(entity_type, entity)

        rattrs = {}
        rattrs["id"] = attrs["id"]
        rattrs["type"] = attrs["type"]
        rattrs["blockchain"] = attrs["authenticationBlockchainUser"]["value"]
        rattrs["location"] = attrs["networkLocation"]["value"]

        if entity_type not in self.app_types:
            rattrs["zone"] = attrs["networkZone"]["value"]

        return rattrs
    
    def parse_payload(self, payload, topic):
        """Decodes the payload and splits the topic

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        return data, split_topic
    
    def process_request(self, split_topic):
        """Decodes the payload and splits the topic

        Args:
            split_topic (str): The split topic.
        """

        entity_type, entity = self.get_entity_details(
            split_topic)

        self.helpers.logger.info(
            "Received " + entity_type  + " status data payload")

        attrs = self.get_attributes(
            entity_type, entity)

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"
        bch = attrs["blockchain"]

        return entity_type, entity, location, zone, bch

    def publish_life(self):
        """ Publishes entity statistics to HIAS. """

        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory()[2]
        hdd = psutil.disk_usage('/hias').percent
        tmp = psutil.sensors_temperatures()['coretemp'][0].current
        r = requests.get('http://ipinfo.io/json?token=' +
                    self.credentials["iotJumpWay"]["ipinfo"])
        data = r.json()

        if "loc" in data:
            location = data["loc"].split(',')
        else:
            location = ["0.0", "0.0"]

        # Send iotJumpWay notification
        self.mqtt.publish("Life", {
            "CPU": str(cpu),
            "Memory": str(mem),
            "Diskspace": str(hdd),
            "Temperature": str(tmp),
            "Latitude": float(location[0]),
            "Longitude": float(location[1])
        })

        self.helpers.logger.info("Agent life statistics published.")
        threading.Timer(300.0, self.publish_life).start()

    def threading(self):
        """ Creates required module threads. """

        # Life thread
        threading.Timer(10.0, self.publish_life).start()

    def respond(self, responseCode, response, accepted):
        """ Builds the request response """

        headers = {}
        if "application/json" in accepted:
            response =  Response(
                response=response, status=responseCode,
                mimetype="application/json")
            headers['Content-Type'] = 'application/json'
        elif "text/plain" in accepted:
            response = self.broker.prepareResponse(response)
            response = Response(
                response=response, status=responseCode,
                    mimetype="text/plain")
            headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers = headers
        return response
    
    @abstractmethod
    def status_callback(self, topic, payload):
        """Called in the event of a status payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
        pass
    
    @abstractmethod
    def life_callback(self, topic, payload):
        """Called in the event of a life payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
        pass
    
    @abstractmethod
    def comands_callback(self, topic, payload):
        """
        iotJumpWay Device Commands Callback

        The callback function that is triggerend in the event of an device
        command communication from the iotJumpWay.

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
        pass

    @abstractmethod
    def notifications_callback(self, topic, payload):
        """Called in the event of an notifications payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
        pass

    @abstractmethod
    def actuators_callback(self, topic, payload):
        """Called in the event of an actuator payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
        pass

    @abstractmethod
    def sensors_callback(self, topic, payload):
        """Called in the event of a sensor payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
            
    @abstractmethod
    def state_callback(self, topic, payload):
        """Called in the event of a state payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """
            
    @abstractmethod
    def classification_callback(self, topic, payload):
        """Called in the event of a classification payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

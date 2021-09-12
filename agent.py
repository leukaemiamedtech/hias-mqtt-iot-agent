#!/usr/bin/env python3
""" HIAS iotJumpWay MQTT IoT Agent

This object represents a HIAS iotJumpWay IoT Agent. HIAS IoT Agents process all
data coming from entities connected to the HIAS iotJumpWay broker using the
MQTT & Websocket machine to machine protocols.

MIT License

Copyright (c) 2021 Asociación de Investigacion en Inteligencia Artificial
Para la Leucemia Peter Moss

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

from gevent import monkey
monkey.patch_all()

import json
import os
import psutil
import signal
import sys
import time

from datetime import datetime
from flask import Flask, request, Response
from threading import Thread

from modules.AbstractAgent import AbstractAgent


class agent(AbstractAgent):
    """ Class representing a HIAS iotJumpWay MQTT IoT Agent.

    This object represents a HIAS iotJumpWay IoT Agent. HIAS IoT Agents
    process all data coming from entities connected to the HIAS iotJumpWay
    broker using the MQTT & Websocket machine to machine protocols.
    """

    def status_callback(self, topic, payload):
        """Called in the event of a status payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        status = payload.decode()
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type  + " Status")

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": status},
                "networkStatus.metadata": {"timestamp": {"value": datetime.now().isoformat()}},
                "dateModified": {"value": datetime.now().isoformat()}
            })

        if update_response:
            _id = self.hiashdi.insert_data("Statuses", {
                "Use": entity_type,
                "Location": location,
                "Zone": zone,
                "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                "Agent": entity if entity_type == "Agent" else "NA",
                "Application": entity if entity_type == "Application" else "NA",
                "Device": entity if entity_type == "Device" else "NA",
                "Staff": entity if entity_type == "Staff" else "NA",
                "Robotics": entity if entity_type == "Robotics" else "NA",
                "Status": status,
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            if _id != False:
                self.helpers.logger.info(
                    entity_type + " " + entity + " status update OK")

                self.mqtt.publish("Integrity", {
                    "_id": str(_id),
                    "Status": status
                })

            else:
                self.helpers.logger.error(
                entity_type + " " + entity + " status update KO")

        else:
            self.helpers.logger.error(
                entity_type + " " + entity + " status update KO")

    def life_callback(self, topic, payload):
        """Called in the event of a life payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type  + " Life")

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": "ONLINE"},
                "networkStatus.metadata": {"timestamp": {"value": datetime.now().isoformat()}},
                "dateModified": {"value": datetime.now().isoformat()},
                "cpuUsage": {
                    "value": float(data["CPU"])
                },
                "memoryUsage": {
                    "value": float(data["Memory"])
                },
                "hddUsage": {
                    "value": float(data["Diskspace"])
                },
                "temperature": {
                    "value": float(data["Temperature"])
                },
                "location": {
                    "type": "geo:json",
                    "value": {
                        "type": "Point",
                        "coordinates": [float(data["Latitude"]), float(data["Longitude"])]
                    }
                }
            })

        if update_response:
            _id = self.hiashdi.insert_data("Life", {
                "Use": entity_type,
                "Location": location,
                "Zone": zone,
                "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                "Agent": entity if entity_type == "Agent" else "NA",
                "Application": entity if entity_type == "Application" else "NA",
                "Device": entity if entity_type == "Device" else "NA",
                "Staff": entity if entity_type == "Staff" else "NA",
                "Robotics": entity if entity_type == "Robotics" else "NA",
                "Data": data,
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            if _id != False:
                self.helpers.logger.info(
                    entity_type + " " + entity + " life update OK")

                self.mqtt.publish("Integrity", {
                    "_id": str(_id),
                    "CPU": str(data["CPU"]),
                    "Memory": str(data["Memory"]),
                    "Diskspace": str(data["Diskspace"]),
                    "Temperature": str(data["Temperature"]),
                    "Latitude": str(data["Latitude"]),
                    "Longitude": str(data["Longitude"])
                })

            else:
                self.helpers.logger.error(
                entity_type + " " + entity + " life update KO")
        else:
            self.helpers.logger.error(
                entity_type + " " + entity + " life update KO")

    def sensors_callback(self, topic, payload):
        """Called in the event of a sensor payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type  + " Sensors Data")

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        sensors = self.hiascdi.get_sensors(
            entity, entity_type)
        sensor_data = sensors["sensors"]

        i = 0
        for sensor in sensor_data["value"]:
            for prop in sensor["properties"]["value"]:
                if data["Type"].lower() in prop:
                    sensor_data["value"][i]["properties"]["value"][data["Type"].lower()] = {
                        "value": data["Value"],
                        "timestamp":  {
                            "value": datetime.now().isoformat()
                        }
                    }
            i = i + 1

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": "ONLINE"},
                "networkStatus.metadata": {"timestamp":  {
                    "value": datetime.now().isoformat()
                }},
                "dateModified": {"value": datetime.now().isoformat()},
                "sensors": sensor_data
            })

        if update_response:
            _id = self.hiashdi.insert_data("Sensors", {
                "Use": entity_type,
                "Location": location,
                "Zone": zone,
                "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                "Agent": entity if entity_type == "Agent" else "NA",
                "Application": entity if entity_type == "Application" else "NA",
                "Device": entity if entity_type == "Device" else "NA",
                "Staff": entity if entity_type == "Staff" else "NA",
                "Robotics": entity if entity_type == "Robotics" else "NA",
                "Sensor": data["Sensor"],
                "Type": data["Type"],
                "Value": data["Value"],
                "Message": data["Message"],
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            if _id != False:
                self.helpers.logger.info(
                    entity_type + " " + entity + " sensors update OK")

                self.mqtt.publish("Integrity", {
                    "_id": str(_id),
                    "Sensor": data["Sensor"],
                    "Type": data["Type"],
                    "Value": data["Value"],
                    "Message": data["Message"]
                })

            else:
                self.helpers.logger.error(
                entity_type + " " + entity + " sensors update KO")
        else:
            self.helpers.logger.error(
                entity_type + " " + entity + " sensors update KO")

    def actuator_callback(self, topic, payload):
        """Called in the event of a actuator payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type  + " Actuators Data")

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        actuators = self.hiascdi.get_actuators(
            entity, entity_type)
        actuator_data = actuators["actuators"]

        i = 0
        for actuator in actuator_data["value"]:
            exists = True
            if data["Name"] in actuator["name"]["value"] and data["Type"].lower() in actuator["commands"]["value"] \
                and data["Value"].lower() in actuator["commands"]["value"][data["Type"].lower()]:
                actuator_data["value"][i]["state"] = {
                    "value": data["Value"],
                    "metadata":{
                        "timestamp": {
                            "value": datetime.now().isoformat()
                        }
                    }
                }
            i = i + 1

        if exists:
            update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": "ONLINE"},
                "networkStatus.metadata": {"timestamp":  {
                    "value": datetime.now().isoformat()
                }},
                "dateModified": {"value": datetime.now().isoformat()},
                "actuators": actuator_data
            })

            if update_response:
                _id = self.hiashdi.insert_data("Actuators", {
                    "Use": entity_type,
                    "Location": location,
                    "Zone": zone,
                    "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                    "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                    "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                    "Agent": entity if entity_type == "Agent" else "NA",
                    "Application": entity if entity_type == "Application" else "NA",
                    "Device": entity if entity_type == "Device" else "NA",
                    "Staff": entity if entity_type == "Staff" else "NA",
                    "Robotics": entity if entity_type == "Robotics" else "NA",
                    "Actuator": data["Name"],
                    "Type": data["Type"],
                    "Value": data["Value"],
                    "Message": data["Message"],
                    "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                if _id != False:
                    self.helpers.logger.info(
                        entity_type + " " + entity + " actuators update OK")

                    self.mqtt.publish("Integrity", {
                        "_id": str(_id),
                        "Actuator": data["Name"],
                        "Type": data["Type"],
                        "Value": data["Value"],
                        "Message": data["Message"]
                    })

                else:
                    self.helpers.logger.error(
                    entity_type + " " + entity + " actuators update KO")
            else:
                self.helpers.logger.error(
                    entity_type + " " + entity + " actuators update KO")

    def comands_callback(self, topic, payload):
        """
        iotJumpWay Device Commands Callback

        The callback function that is triggerend in the event of an device
        command communication from the iotJumpWay.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received Command Data")

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"
        exists = False

        if "Command" in data and data["Command"] == "Verify":

            if data["Use"] == "Device":

                actuators = self.hiascdi.get_actuators(
                     data["To"], data["Use"])
                actuator_data = actuators["actuators"]

                i = 0
                for actuator in actuator_data["value"]:
                    exists = True
                    if data["Name"] in actuator["name"]["value"] and data["Type"].lower() in actuator["commands"]["value"] \
                        and data["Value"].lower() in actuator["commands"]["value"][data["Type"].lower()]:
                        actuator_data["value"][i]["state"] = {
                            "value": "Processing " + data["Value"],
                            "metadata":{
                                "timestamp": {
                                    "value": datetime.now().isoformat()
                                }
                            }
                        }
                    i = i + 1

                if exists:
                    update_response = self.hiascdi.update_entity(
                    data["To"], data["Use"], {
                        "networkStatus": {"value": "ONLINE"},
                        "networkStatus.metadata": {"timestamp":  {
                            "value": datetime.now().isoformat()
                        }},
                        "dateModified": {"value": datetime.now().isoformat()},
                        "actuators": actuator_data
                    })

                    pathto = location + "/Devices/" +  data["Zone"] \
                        + "/" + data["To"] + "/Commands"

                    self.mqtt.publish("Custom", {
                        "From": entity,
                        "Type": data["Type"],
                        "Name": data["Name"],
                        "Value": data["Value"],
                        "Message": data["Message"]
                    }, pathto)

                    _id = self.hiashdi.insert_data("Commands", {
                        "Use": data["Use"],
                        "From": data["From"],
                        "Location": location,
                        "Zone": data["Zone"],
                        "HIASBCH": "NA",
                        "HIASCDI": "NA",
                        "HIASHDI": "NA",
                        "Agent": "NA",
                        "Application": "NA",
                        "Device": data["To"],
                        "Staff":"NA",
                        "Robotics": "NA",
                        "Actuator": data["Name"],
                        "Type": data["Type"],
                        "Value": data["Value"],
                        "Message": data["Message"],
                        "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })

                    self.mqtt.publish("Integrity", {
                        "_id": str(_id),
                        "From": data["From"],
                        "Actuator": data["Name"],
                        "Type": data["Type"],
                        "Value": data["Value"],
                        "Message": data["Message"]
                    })

                    self.helpers.logger.info(
                        data["Use"] + " " + data["To"] + " command update OK")

    def bci_callback(self, topic, payload):
        """Called in the event of a BCI payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type + " BCI Data: " + str(data))

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "network.status": {"value": "ONLINE"},
                "network.status.metadata": {"timestamp": datetime.now().isoformat()},
                "dateModified": {"value": datetime.now().isoformat()}
            })

        if update_response:
            _id = self.hiashdi.insert_data("Sensors", {
                "Use": entity_type,
                "Location": location,
                "Zone": zone,
                "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                "Agent": entity if entity_type == "Agent" else "NA",
                "Application": entity if entity_type == "Application" else "NA",
                "Device": entity if entity_type == "Device" else "NA",
                "Staff": entity if entity_type == "Staff" else "NA",
                "Robotics": entity if entity_type == "Robotics" else "NA",
                "Sensor": data["Sensor"],
                "Type": data["Type"],
                "Value": data["Value"],
                "Message": data["Message"],
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            self.mqtt.publish("Integrity", {
                "_id": str(_id),
                "Sensor": data["Sensor"],
                "Type": data["Type"],
                "Value": data["Value"],
                "Message": data["Message"]
            })

            self.helpers.logger.info(
                entity_type + " " + entity + " BCI data update OK")
        else:
            self.helpers.logger.error(
                entity_type + " " + entity + " BCI data update KO")

    def ai_model_callback(self, topic, payload):
        """Called in the event of an AI payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type + " AI Data: " + str(data))

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "network.status": {"value": "ONLINE"},
                "network.status.metadata": {"timestamp": datetime.now().isoformat()},
                "dateModified": {"value": datetime.now().isoformat()}
            })

        models = self.hiascdi.get_ai_models(entity, entity_type)
        model_data = models["models"]["value"]
        modelExists = False

        for model in model_data:
            modelExists = True
            if model == data["Model"] and data["State"] in model_data[data["Model"]]["states"]["value"]:
                model_data[data["Model"]]["state"] = {
                    "value": data["State"],
                    "timestamp": datetime.now().isoformat()
                }
            if model == data["Model"] and data["Type"] in model_data[data["Model"]]["properties"]["value"]:
                model_data[data["Model"]]["properties"]["value"][data["Type"]] = {
                    "value": data["Value"],
                    "timestamp": datetime.now().isoformat()
                }

        if modelExists:
            update_response = self.hiascdi.update_entity(
                entity, entity_type, {
                    "models": {"value": model_data},
                    "dateModified": {"value": datetime.now().isoformat()}
                })

            if update_response:
                _id = self.hiashdi.insert_data("AI", {
                    "Use": entity_type,
                    "Location": location,
                    "Zone": zone,
                    "Agent": entity,
                    "Type": data["Type"],
                    "Value": data["Value"],
                    "Message": data["Message"],
                    "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                self.helpers.logger.info(
                    entity_type + " " + entity + " AI model data update OK")
            else:
                self.helpers.logger.error(
                    entity_type + " " + entity + " AI model data update KO")

    def state_callback(self, topic, payload):
        """Called in the event of an state payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))
        split_topic = topic.split("/")

        if split_topic[1] not in self.ignore_types:
            entity_type = split_topic[1][:-1]
        else:
            entity_type = split_topic[1]

        if entity_type in ["Robotics", "Application", "Staff"]:
            entity = split_topic[2]
        else:
            entity = split_topic[3]

        self.helpers.logger.info(
            "Received " + entity_type + " State Data: " + str(data))

        attrs = self.get_attributes(entity_type, entity)
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]
        zone = attrs["zone"] if "zone" in attrs else "NA"

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "network.status": {"value": "ONLINE"},
                "network.status.metadata": {"timestamp": datetime.now().isoformat()},
                "dateModified": {
                    "type": "DateTime",
                    "value": datetime.now().isoformat()
                }
            })

        actuators = self.hiascdi.get_actuators(entity, entity_type)
        actuator_data = actuators["actuators"]["value"]
        exists = False

        i = 0
        for actuator in actuator_data:
            exists = True
            if data["Name"] in actuator["name"]["value"] and data["Type"].lower() in actuator["commands"] \
                and data["Value"].lower() in actuator["commands"][data["Type"]]:
                actuator_data[i]["state"] = {
                    "value": data["Value"],
                    "timestamp": datetime.now().isoformat()
                }
            i = i + 1

        if exists:
            update_response = self.hiascdi.update_entity(
                entity, entity_type, {
                    "actuators": {"value": actuator_data},
                    "dateModified": {
                        "type": "DateTime",
                        "value": datetime.now().isoformat()
                    }
                })

            if update_response:
                _id = self.hiashdi.insert_data("Actuators", {
                    "Use": entity_type,
                    "Location": location,
                    "Zone": zone,
                    "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                    "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                    "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                    "Agent": entity if entity_type == "Agent" else "NA",
                    "Application": entity if entity_type == "Application" else "NA",
                    "Device": entity if entity_type == "Device" else "NA",
                    "Staff": entity if entity_type == "Staff" else "NA",
                    "Robotics": entity if entity_type == "Robotics" else "NA",
                    "Actuator": data["Name"],
                    "Type": data["Type"],
                    "Value": data["Value"],
                    "Message": data["Message"],
                    "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                self.mqtt.publish("Integrity", {
                    "_id": str(_id),
                    "From": entity,
                    "Actuator": data["Name"],
                    "Type": data["Type"],
                    "Value": data["Value"],
                    "Message": data["Message"]
                })

                self.helpers.logger.info(
                    entity_type + " " + entity + " state data update OK")
            else:
                self.helpers.logger.error(
                    entity_type + " " + entity + " state data update KO")

    def respond(self, responseCode, response):
        """ Returns the request repsonse """

        return Response(response=json.dumps(response, indent=4),
                        status=responseCode,
                        mimetype="application/json")

    def signal_handler(self, signal, frame):
        self.helpers.logger.info("Disconnecting")
        self.mqtt.disconnect()
        sys.exit(1)

app = Flask(__name__)
agent = agent()

@app.route('/About', methods=['GET'])
def about():
    """
    Returns Agent details
    Responds to GET requests sent to the North Port About API endpoint.
    """

    return agent.respond(200, {
        "Identifier": agent.credentials["iotJumpWay"]["entity"],
        "Host": agent.credentials["server"]["ip"],
        "NorthPort": agent.credentials["server"]["port"],
        "CPU": psutil.cpu_percent(),
        "Memory": psutil.virtual_memory()[2],
        "Diskspace": psutil.disk_usage('/').percent,
        "Temperature": psutil.sensors_temperatures()['coretemp'][0].current
    })

def main():

    signal.signal(signal.SIGINT, agent.signal_handler)
    signal.signal(signal.SIGTERM, agent.signal_handler)

    agent.hiascdi_connection()
    agent.hiashdi_connection()
    agent.hiasbch_connection()
    agent.mqtt_connection({
        "host": agent.credentials["iotJumpWay"]["host"],
        "port": agent.credentials["iotJumpWay"]["port"],
        "location": agent.credentials["iotJumpWay"]["location"],
        "zone": agent.credentials["iotJumpWay"]["zone"],
        "entity": agent.credentials["iotJumpWay"]["entity"],
        "name": agent.credentials["iotJumpWay"]["name"],
        "un": agent.credentials["iotJumpWay"]["un"],
        "up": agent.credentials["iotJumpWay"]["up"]
    })

    agent.mqtt.actuator_callback = agent.actuator_callback
    agent.mqtt.ai_model_callback = agent.ai_model_callback
    agent.mqtt.bci_callback = agent.bci_callback
    agent.mqtt.comands_callback = agent.comands_callback
    agent.mqtt.life_callback = agent.life_callback
    agent.mqtt.sensors_callback = agent.sensors_callback
    agent.mqtt.state_callback = agent.state_callback
    agent.mqtt.status_callback = agent.status_callback

    agent.threading()

    app.run(host=agent.helpers.credentials["server"]["ip"],
            port=agent.helpers.credentials["server"]["port"])

if __name__ == "__main__":
    main()

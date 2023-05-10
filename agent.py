#!/usr/bin/env python3
""" HIAS iotJumpWay MQTT IoT Agent

This object represents a HIAS iotJumpWay IoT Agent. HIAS IoT Agents process all
data coming from entities connected to the HIAS iotJumpWay broker using the
MQTT & Websocket machine to machine protocols.

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

from gevent import monkey
monkey.patch_all()

import json
import psutil
import signal
import sys

from bson import json_util
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

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return
        
        update_response = self.hiascdi.update_online_status(
            entity, entity_type, status)

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " status update KO")
            return

        update_data = self.hiashdi.entity_status_data(
            entity, entity_type, location, zone, status)
        
        _id = self.hiashdi.insert_data(
            "Statuses", update_data)
            
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " status data update KO")
            return
            
        update_data["_id"] = _id
        self.mqtt.publish(
            "Integrity", update_data)
        
        self.helpers.logger.info(
            entity_type + " " + entity + " status data update OK")

    def life_callback(self, topic, payload):
        """Called in the event of a life payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        update_response = self.hiascdi.update_entity(
            entity, entity_type, self.hiascdi.entity_life_data(data))

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " life update KO")
            return
        
        update_data = self.hiashdi.entity_life_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data(
            "Life", update_data)
        
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " life update KO")
            return

        self.mqtt.publish("Integrity", {
            "_id": str(_id),
            "CPU": str(data["CPU"]),
            "Memory": str(data["Memory"]),
            "Diskspace": str(data["Diskspace"]),
            "Temperature": str(data["Temperature"]),
            "Latitude": str(data["Latitude"]),
            "Longitude": str(data["Longitude"])
        })

        self.helpers.logger.info(
            entity_type + " " + entity + " life update OK")

    def comands_callback(self, topic, payload):
        """
        iotJumpWay Device Commands Callback

        The callback function that is triggerend in the event of an device
        command communication from the iotJumpWay.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return
        
        if "Use" not in data:
            self.helpers.logger.error(
                "Command not supported yet")
            return
        
        if data["Use"] != "Device":
            self.helpers.logger.error(
                "Command not supported yet")
            return

        entity_data = self.hiascdi.get_entity(
            data["Use"], data["To"])
        
        if data["Property"] not in entity_data:
            self.helpers.logger.error(
                "Property not found")
            return
        
        if data["Type"] not in entity_data[data["Property"]]["metadata"]["commands"]["value"]:
            self.helpers.logger.error(
                "Command not found")
            return
        
        if data["Value"] not in entity_data[data["Property"]]["metadata"]["commands"]["value"][data["Type"]]:
            self.helpers.logger.error(
                "Command not found")
            return
        
        actuator_data = self.hiascdi.entity_actuator_data(
            entity_data, data)

        self.hiascdi.update_entity(
            data["To"], data["Use"], {
                data["Type"]: actuator_data,
                "dateModified": {"value": datetime.now().isoformat()}
            })

        pathto = location + "/Devices/" +  data["Zone"] \
            + "/" + data["To"] + "/Commands"

        self.mqtt.publish("Custom", {
            "Type": data["Type"],
            "Property": data["Property"],
            "Value": data["Value"],
            "Message": data["Message"]
        }, pathto)

        update_data = self.hiashdi.entity_actuator_command_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data("Commands", update_data)
            
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " command data update KO")
            return
        
        update_data["_id"] = _id
        self.mqtt.publish("Integrity", update_data)

        self.helpers.logger.info(
            entity_type + " " + entity + " command data update OK")

    def notifications_callback(self, topic, payload):
        """Called in the event of an notifications payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data = json.loads(payload.decode("utf-8"))

        self.helpers.logger.info(
            "Received " + data["Use"]  + " notifications data payload")

        attrs = self.get_attributes(
            data["FromType"], data["From"])
        bch = attrs["blockchain"]

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity = attrs["id"]
        location = attrs["location"]

        update_data = self.hiashdi.entity_notification_data(
            location, data)

        _id = self.hiashdi.insert_data(
            "Notifications", update_data)
            
        if _id == False:
            self.helpers.logger.error(
                data["Use"] + " " + data["To"] + " notification update KO")
            return

        update_data["_id"] = _id
        self.mqtt.publish("Integrity", update_data)

        self.helpers.logger.info(
            data["Use"] + " " + data["To"] + " notification update OK")

    def actuators_callback(self, topic, payload):
        """Called in the event of a actuator payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity_data = self.hiascdi.get_entity(
            entity_type, entity)
        
        if data["Type"] not in entity_data:
            self.helpers.logger.error(
                entity_type + " " + entity + " actuators not found")
            return 

        actuator_data = self.hiascdi.entity_actuator_data(
            entity_data, data)

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": "ONLINE"},
                "networkStatus.metadata": {"timestamp":  {
                    "value": datetime.now().isoformat()
                }},
                data["Type"]: actuator_data,
                "dateModified": {"value": datetime.now().isoformat()}
            })

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " actuators update KO")
            return

        update_data = self.hiashdi.entity_actuator_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data("Actuators", update_data)
            
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " actuators update KO")
            return

        update_data["_id"] = _id
        self.mqtt.publish(
            "Integrity", update_data)
        
        self.helpers.logger.info(
            entity_type + " " + entity + " actuators update OK")

    def sensors_callback(self, topic, payload):
        """Called in the event of a sensor payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return

        entity_data = self.hiascdi.get_entity(
            entity_type, entity)
        
        if data["Type"] not in entity_data:
            self.helpers.logger.error(
                entity_type + " " + entity + " sensors not found")
            return 

        sensor_data = self.hiascdi.entity_sensor_data(
            entity_data, data)

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": "ONLINE"},
                "networkStatus.metadata": {"timestamp":  {
                    "value": datetime.now().isoformat()
                }},
                "dateModified": {"value": datetime.now().isoformat()},
                data["Type"]: sensor_data
            })

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " sensors update KO")
            return

        update_data = self.hiashdi.entity_sensor_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data("Sensors", update_data)
            
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " sensors update KO")
            return
        
        update_data["_id"] = _id
        self.mqtt.publish("Integrity", update_data)
        
        self.helpers.logger.info(
            entity_type + " " + entity + " sensors data update OK")
            
    def state_callback(self, topic, payload):
        """Called in the event of a state payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return
        
        update_response = self.hiascdi.update_online_status(
            entity, entity_type, "ONLINE")

        entity_data = self.hiascdi.get_entity(
            entity_type, entity)
        
        if data["State"] not in entity_data["states"]["value"]:
            self.helpers.logger.error(
                entity_type + " " + entity + " state update KO")
            return
        
        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "state": {"value": data["State"]},
                "dateModified": {"value": datetime.now().isoformat()}
            })

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " state update KO")
            return
        
        update_data = self.hiashdi.entity_state_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data(
            "State", update_data)
        
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " state update KO")
            return
        
        update_data["_id"] = _id
        self.mqtt.publish(
            "Integrity", update_data)
        
        self.helpers.logger.info(
            entity_type + " " + entity + " state update OK")
            
    def classification_callback(self, topic, payload):
        """Called in the event of a classification payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return
        
        update_response = self.hiascdi.update_online_status(
            entity, entity_type, "ONLINE")

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " AI model update KO")
            return

        models = self.hiascdi.get_ai_models(
            entity, entity_type)
        
        model_data = models["models"]["value"]
        modelExists = False

        newModelData = []
        
        if model_data is None:
            self.helpers.logger.error(
                entity_type + " " + entity + " does not have any models")
            return

        for model in model_data:
            modelExists = True
            if model["model"] == data["Model"]:
                if "State" in data and data["State"] in model["context"]["states"]["value"]:
                    model["context"]["state"] = {
                        "value": data["State"],
                        "timestamp": datetime.now().isoformat()
                    }
                if "Type" in data and data["Type"] in model["context"]["properties"]["value"]:
                    model["context"]["properties"]["value"][data["Type"]] = {
                        "value": data["Value"],
                        "timestamp": datetime.now().isoformat()
                    }
                newModelData.append(model)
        
        if modelExists == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " does not have a " + data["Model"] + " model")
            return

        update_response = self.hiascdi.update_entity(
            entity, entity_type, {
                "models": {"value": newModelData},
                "dateModified": {"value": datetime.now().isoformat()}
            })

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " AI model update KO")
            return
        
        update_data = self.hiashdi.entity_ai_model_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data(
            "Classification", update_data)
        
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " AI model update KO")
            return
        
        update_data["_id"] = _id
        self.mqtt.publish("Integrity", update_data)
        self.helpers.logger.info(
            entity_type + " " + entity + " AI model update OK")

    def bci_callback(self, topic, payload):
        """Called in the event of a BCI payload

        Args:
            topic (str): The topic the payload was sent to.
            payload (:obj:`str`): The payload.
        """

        data, split_topic = self.parse_payload(
            payload, topic)

        entity_type, entity, location, zone, bch = self.process_request(
            split_topic)

        if not self.hiasbch.iotjumpway_access_check(bch):
            return
        
        update_response = self.hiascdi.update_online_status(
            entity, entity_type, "ONLINE")

        if update_response == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " AI model update KO")
            return

        update_data = self.hiashdi.entity_bci_data(
            entity, entity_type, location, zone, data)
        
        _id = self.hiashdi.insert_data(
            "Sensors", update_data)
        
        if _id == False:
            self.helpers.logger.error(
                entity_type + " " + entity + " BCI update KO")
            return
        
        update_data["_id"] = _id
        self.mqtt.publish(
            "Integrity", update_data)
        
        self.helpers.logger.info(
            entity_type + " " + entity + " BCI update OK")

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

@app.route('/Rules', methods=['POST'])
def rules():
    """
    Returns Agent details
    Responds to GET requests sent to the North Port About API endpoint.
    """

    accepted = agent.check_accepts_type(request.headers)
    content_type = agent.check_content_type(request.headers)
    query = agent.check_body(request)

    if accepted is False:
        return agent.respond(
            406, agent.confs["errorMessages"][str(406)],
            "application/json")

    if content_type is False:
        return agent.respond(
            415, agent.confs["errorMessages"][str(415)],
            "application/json")

    if query is False:
        return agent.respond(
            400, agent.confs["errorMessages"]["400p"],
            accepted)

    entities = query["data"]
    entity = agent.hiascdi.get_entity(
        entities[0]["type"], entities[0]["id"])

    for rule in entity["rules"]["value"]:
        if rule["subscription"] == query["subscriptionId"]:
            break

    if rule["action"]["type"] == 'staff_ui':
        message = entity["name"]["value"]
        if rule["event"]["type"] == 'sensors':
            message += " " + rule["event"]["sensor"]
        if rule["event"]["type"] == 'actuators':
            message += " " + rule["event"]["actuator"]
        message += " is " + rule["event"]["range"] + " " + rule["event"]["value"]

        pathto = entity["networkLocation"]["value"] + "/Staff/" \
            +  rule["action"]["user"] + "/Notifications"

        Thread(target=agent.mqtt.publish, args=(
            "Custom", {
                "Use": "Staff",
                "From": entities[0]["id"],
                "FromType": entities[0]["type"],
                "To": rule["action"]["user"],
                "Message": message
            }, pathto), daemon=True).start()

    elif rule["action"]["type"] == 'output_device_command':

        device = agent.hiascdi.get_entity(
            "Device", rule["action"]["device"])

        if device[rule["action"]["property"]]["value"] != rule["action"]["value"]:

            pathto = agent.credentials["iotJumpWay"]["location"] + "/Agents/" \
                +  agent.credentials["iotJumpWay"]["zone"] + "/" +  agent.credentials["iotJumpWay"]["entity"] + "/Commands"

            Thread(target=agent.mqtt.publish, args=(
                "Custom", {
                    "Use": "Device",
                    "To": device["id"],
                    "Zone": device["networkZone"]["value"],
                    "Property": rule["action"]["property"],
                    "Type": rule["action"]["command"],
                    "Value": rule["action"]["value"],
                    "Message": rule["action"]["command"].capitalize() + " " + rule["action"]["value"]
                }, pathto), daemon=True).start()

    return agent.respond(
        200, json.dumps(json.loads(
                json_util.dumps(entity))), accepted)

def main():

    signal.signal(signal.SIGINT, agent.signal_handler)
    signal.signal(signal.SIGTERM, agent.signal_handler)

    agent.hiascdi_connection()
    agent.hiashdi_connection()
    agent.hiasbch_connection()
    agent.mqtt_connection({
        "host": agent.credentials["iotJumpWay"]["host"],
        "port": agent.credentials["iotJumpWay"]["port"],
        "security": agent.confs["agent"]["secure"],
        "location": agent.credentials["iotJumpWay"]["location"],
        "zone": agent.credentials["iotJumpWay"]["zone"],
        "entity": agent.credentials["iotJumpWay"]["entity"],
        "name": agent.credentials["iotJumpWay"]["name"],
        "un": agent.credentials["iotJumpWay"]["un"],
        "up": agent.credentials["iotJumpWay"]["up"]
    })

    agent.mqtt.actuators_callback = agent.actuators_callback
    agent.mqtt.bci_callback = agent.bci_callback
    agent.mqtt.comands_callback = agent.comands_callback
    agent.mqtt.classification_callback = agent.classification_callback 
    agent.mqtt.life_callback = agent.life_callback
    agent.mqtt.notifications_callback = agent.notifications_callback
    agent.mqtt.sensors_callback = agent.sensors_callback
    agent.mqtt.state_callback = agent.state_callback
    agent.mqtt.status_callback = agent.status_callback

    agent.threading()

    app.run(host=agent.helpers.credentials["server"]["ip"],
            port=agent.helpers.credentials["server"]["port"])

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
""" HIASHDI Helper Module

This module provides helper functions that allow the HIAS IoT Agents
to communicate with the HIASHDI Historical Data Interface.

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
import requests

from datetime import datetime


class hiashdi():
    """ HIASHDI Helper Module

    This module provides helper functions that allow the HIAS IoT
    Agents to communicate with the HIASHDI Historical Data Interface.
    """

    def __init__(self, helpers):
        """ Initializes the class. """

        self.helpers = helpers
        self.program = "HIASHDI Helper Module"

        self.headers = {
            "accept": self.helpers.confs["agent"]["api"]["content"],
            "content-type": self.helpers.confs["agent"]["api"]["content"]
        }

        self.auth = (self.helpers.credentials["hiashdi"]["un"],
                    self.helpers.confs["agent"]["proxy"]["up"])

        self.helpers.logger.info("HIASHDI initialization complete.")

    def insert_data(self, typeof, data):
        """ Inserts data into HIASHDI. """

        api_host = "http://" + self.helpers.credentials["server"]["host"] + "/" + \
                    self.helpers.credentials["hiashdi"]["endpoint"]
        api_endpoint = "/data?type=" + typeof
        api_url = api_host + api_endpoint

        response = requests.post(api_url, data=json.dumps(
            data), headers=self.headers, auth=self.auth)

        if response.status_code == 201:
            return response.headers["Id"]
        else:
            return False
        
    def entity_status_data(self, entity, entity_type, location, zone, status):
        
        return {
            "Use": entity_type,
            "Location": location,
            "Zone": zone,
            "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
            "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
            "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
            "Agent": entity if entity_type == "Agent" else "NA",
            "AiAgent": entity if entity_type == "AiAgent" else "NA",
            "Application": entity if entity_type == "Application" else "NA",
            "Device": entity if entity_type == "Device" else "NA",
            "Staff": entity if entity_type == "Staff" else "NA",
            "Robotics": entity if entity_type == "Robotics" else "NA",
            "Status": status,
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_life_data(self, entity, entity_type, location, zone, data):
        
        return {
            "Use": entity_type,
            "Location": location,
            "Zone": zone,
            "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
            "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
            "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
            "Agent": entity if entity_type == "Agent" else "NA",
            "AiAgent": entity if entity_type == "AiAgent" else "NA",
            "Application": entity if entity_type == "Application" else "NA",
            "Device": entity if entity_type == "Device" else "NA",
            "Staff": entity if entity_type == "Staff" else "NA",
            "Robotics": entity if entity_type == "Robotics" else "NA",
            "Data": data,
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_actuator_data(self, entity, entity_type, location, zone, data):
        
        return {
            "Use": entity_type,
            "Location": location,
            "Zone": zone,
            "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
            "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
            "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
            "Agent": entity if entity_type == "Agent" else "NA",
            "AiAgent": entity if entity_type == "AiAgent" else "NA",
            "Application": entity if entity_type == "Application" else "NA",
            "Device": entity if entity_type == "Device" else "NA",
            "Staff": entity if entity_type == "Staff" else "NA",
            "Robotics": entity if entity_type == "Robotics" else "NA",
            "Actuator": data["Name"],
            "Type": data["Type"],
            "Value": data["Value"],
            "Message": data["Message"],
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_actuator_command_data(self, entity, entity_type, location, zone, data):
        
        return {
            "Use": data["Use"],
            "From": entity,
            "Location": location,
            "Zone": zone,
            "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
            "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
            "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
            "Agent": entity if entity_type == "Agent" else "NA",
            "AiAgent": entity if entity_type == "AiAgent" else "NA",
            "Application": entity if entity_type == "Application" else "NA",
            "Device": entity if entity_type == "Device" else "NA",
            "Staff": entity if entity_type == "Staff" else "NA",
            "Robotics": entity if entity_type == "Robotics" else "NA",
            "Property": data["Property"],
            "Type": data["Type"],
            "Value": data["Value"],
            "Message": data["Message"],
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_sensor_data(self, entity, entity_type, location, zone, data):
        
        return {
            "Use": entity_type,
            "Location": location,
            "Zone": zone,
            "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
            "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
            "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
            "Agent": entity if entity_type == "Agent" else "NA",
            "AiAgent": entity if entity_type == "AiAgent" else "NA",
            "Application": entity if entity_type == "Application" else "NA",
            "Device": entity if entity_type == "Device" else "NA",
            "Staff": entity if entity_type == "Staff" else "NA",
            "Robotics": entity if entity_type == "Robotics" else "NA",
            "Sensor": data["Sensor"],
            "Type": data["Type"],
            "Value": data["Value"],
            "Message": data["Message"],
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_notification_data(self, entity, entity_type, location, zone, data):
        
        return {
            "Use": entity_type,
            "Location": location,
            "Zone": zone,
            "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
            "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
            "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
            "Agent": entity if entity_type == "Agent" else "NA",
            "AiAgent": entity if entity_type == "AiAgent" else "NA",
            "Application": entity if entity_type == "Application" else "NA",
            "Device": entity if entity_type == "Device" else "NA",
            "Staff": entity if entity_type == "Staff" else "NA",
            "Robotics": entity if entity_type == "Robotics" else "NA",
            "Type": data["Type"],
            "Value": data["State"],
            "Message": data["Message"],
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_ai_model_data(self, entity, entity_type, location, zone, data):
        
        return {
            "Use": entity_type,
            "Location": location,
            "Zone": zone,
            "AiAgent": entity,
            "Type": data["Type"] if "Type" in data else "State",
            "Value": data["Value"] if "Value" in data else data["State"],
            "Message": data["Message"],
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_state_data(self, entity, entity_type, location, zone, data):
        return {
                "Use": entity_type,
                "Location": location,
                "Zone": zone,
                "HIASBCH": entity if entity_type == "HIASBCH" else "NA",
                "HIASCDI": entity if entity_type == "HIASCDI" else "NA",
                "HIASHDI": entity if entity_type == "HIASHDI" else "NA",
                "Agent": entity if entity_type == "Agent" else "NA",
                "AiAgent": entity if entity_type == "AiAgent" else "NA",
                "Application": entity if entity_type == "Application" else "NA",
                "Device": entity if entity_type == "Device" else "NA",
                "Staff": entity if entity_type == "Staff" else "NA",
                "Robotics": entity if entity_type == "Robotics" else "NA",
                "Type": data["Type"],
                "Value": data["State"],
                "Message": data["Message"],
                "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
    def entity_notification_data(self, location, data):
        
        return {
            "Use": data["Use"],
            "From": data["From"],
            "To": data["To"],
            "Location": location,
            "Application": data["To"] if data["Use"] == "Application" else "NA",
            "Staff": data["To"] if data["Use"] == "Application" else "NA",
            "Message": data["Message"],
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def entity_bci_data(self, entity, entity_type, location, zone, data):
        return {
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
        }
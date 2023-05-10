#!/usr/bin/env python3
""" HIASCDI Helper Module

This module provides helper functions that allow the HIAS IoT Agents
to communicate with the HIASCDI Context Data Interface.

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

class hiascdi():
    """ HIASCDI Helper Module

    This module provides helper functions that allow the HIAS IoT
    Agents to communicate with the HIASCDI Context Data Interface.
    """

    def __init__(self, helpers):
        """ Initializes the class. """

        self.helpers = helpers
        self.program = "HIASCDI Helper Module"

        self.headers = {
            "accept": self.helpers.confs["agent"]["api"]["content"],
            "content-type": self.helpers.confs["agent"]["api"]["content"]
        }

        self.auth = (self.helpers.credentials["hiascdi"]["un"],
                    self.helpers.confs["agent"]["proxy"]["up"])

        self.helpers.logger.info("HIASCDI initialization complete.")

    def get_attributes(self, entity_type, entity):
        """ Gets required attributes. """

        if entity_type in ["Robotics","Application","Staff"]:
            params = "&attrs=id,type,authenticationBlockchainUser.value,networkLocation.value"
        else:
            params = "&attrs=id,type,authenticationBlockchainUser.value,networkLocation.value,networkZone.value"

        api_host = "http://" + self.helpers.credentials["server"]["host"] + \
                    self.helpers.credentials["hiascdi"]["endpoint"]
        api_endpoint = "/entities/" + entity + "?type=" + entity_type + params
        api_url = api_host + api_endpoint

        response = requests.get(api_url, headers=self.headers, auth=self.auth)

        return json.loads(response.text)

    def get_entity(self, entity_type, entity):
        """ Gets required attributes. """

        api_host = "http://" + self.helpers.credentials["server"]["host"] + \
                    self.helpers.credentials["hiascdi"]["endpoint"]
        api_endpoint = "/entities/" + entity + "?type=" + entity_type
        api_url = api_host + api_endpoint

        response = requests.get(api_url, headers=self.headers, auth=self.auth)

        return json.loads(response.text)

    def update_entity(self, _id, typer, data):
        """ Updates an entity. """

        api_url = "http://" + self.helpers.credentials["server"]["host"] + "/" + \
                    self.helpers.credentials["hiascdi"]["endpoint"] + \
                    "/entities/" + _id + "/attrs?type=" + typer

        response = requests.post(api_url, data=json.dumps(
            data), headers=self.headers, auth=self.auth)

        if response.status_code == 204:
            return True
        else:
            return False

    def get_sensors(self, _id, typeof):
        """ Gets sensor list. """

        api_url = "http://" + self.helpers.credentials["server"]["host"] + "/" + \
                    self.helpers.credentials["hiascdi"]["endpoint"] + \
                    "/entities/" + _id + "?type=" + typeof + "&attrs=sensors"

        response = requests.get(api_url, headers=self.headers, auth=self.auth)

        return json.loads(response.text)

    def get_actuators(self, _id, typeof):
        """ Gets actuator list. """

        api_url = "http://" + self.helpers.credentials["server"]["host"] + "/" + \
                    self.helpers.credentials["hiascdi"]["endpoint"] + \
                    "/entities/" + _id + "?type=" + typeof + "&attrs=actuators"

        response = requests.get(api_url, headers=self.headers, auth=self.auth)

        return json.loads(response.text)

    def get_ai_models(self, _id, typeof):
        """ Gets AI Agent models. """

        api_url = "http://" + self.helpers.credentials["server"]["host"] + "/" + \
                    self.helpers.credentials["hiascdi"]["endpoint"] + \
                    "/entities/" + _id + "?type=" + typeof + "&attrs=models"

        response = requests.get(api_url, headers=self.headers, auth=self.auth)

        return json.loads(response.text)
    
    def update_online_status(self, entity, entity_type, status):
        """Updates the status of an entity

        Args:
            entity (str): The entity ID.
            entity_type (str): The entity type.
            status (str): The entity status.
        """

        return self.update_entity(
            entity, entity_type, {
                "networkStatus": {"value": status},
                "networkStatus.metadata": {"timestamp": {"value": datetime.now().isoformat()}},
                "dateModified": {"value": datetime.now().isoformat()}
            })
        
    def entity_life_data(self,data):
        
        return {
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
            }
        
    def entity_actuator_data(self, entity_data, data):
    
        return {
                "value": "Processing",
                "type": entity_data[data["Property"]]["type"],
                "metadata": {
                    "property": {
                        "value": entity_data[data["Property"]]["metadata"]["property"]["value"]
                    },
                    "propertyId": {
                        "value": entity_data[data["Property"]]["metadata"]["propertyId"]["value"]
                    },
                    "propertyType": {
                        "value": entity_data[data["Property"]]["metadata"]["propertyType"]["value"]
                    },
                    "propertyName": {
                        "value": entity_data[data["Property"]]["metadata"]["propertyName"]["value"]
                    },
                    "commands": {
                        "value": entity_data[data["Property"]]["metadata"]["commands"]["value"]
                    },
                    "description": {
                        "value": entity_data[data["Property"]]["metadata"]["description"]["value"]
                    },
                    "timestamp":  {
                        "value": datetime.now().isoformat()
                    }
                }
            }
        
    def entity_sensor_data(self, entity_data, data):
    
        return {
            "value": data["Value"],
            "type": entity_data[data["Type"]]["type"],
            "metadata": {
                "property": {
                    "value": entity_data[data["Type"]]["metadata"]["property"]["value"]
                },
                "propertyId": {
                    "value": entity_data[data["Type"]]["metadata"]["propertyId"]["value"]
                },
                "propertyType": {
                    "value": entity_data[data["Type"]]["metadata"]["propertyType"]["value"]
                },
                "propertyName": {
                    "value": entity_data[data["Type"]]["metadata"]["propertyName"]["value"]
                },
                "commands": {
                    "value": entity_data[data["Type"]]["metadata"]["commands"]["value"]
                },
                "description": {
                    "value": entity_data[data["Type"]]["metadata"]["description"]["value"]
                },
                "timestamp":  {
                    "value": datetime.now().isoformat()
                }
            }
        }
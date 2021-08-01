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

from abc import ABC, abstractmethod
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

	def statusCallback(self, topic, payload):
		"""Called in the event of a status payload

		Args:
			topic (str): The topic the payload was sent to.
			payload (:obj:`str`): The payload.
		"""

		status = payload.decode()
		splitTopic = topic.split("/")

		if splitTopic[1] not in self.ignoreTypes:
			entityType = splitTopic[1][:-1]
		else:
			entityType = splitTopic[1]

		if entityType in ["Robotics", "Application", "Staff"]:
			entity = splitTopic[2]
		else:
			entity = splitTopic[3]

		self.helpers.logger.info(
			"Received " + entityType  + " Status")

		attrs = self.getRequiredAttributes(entityType, entity)
		bch = attrs["blockchain"]

		if not self.hiasbch.iotJumpWayAccessCheck(bch):
			return

		entity = attrs["id"]
		location = attrs["location"]
		zone = attrs["zone"] if "zone" in attrs else "NA"

		updateResponse = self.hiascdi.updateEntity(
			entity, entityType, {
				"networkStatus": {"value": status},
				"networkStatus.metadata": {"timestamp": {"value": datetime.now().isoformat()}},
				"dateModified": {"value": datetime.now().isoformat()}
			})

		if updateResponse:
			_id = self.hiashdi.insertData("Statuses", {
				"Use": entityType,
				"Location": location,
				"Zone": zone,
				"HIASCDI": entity if entityType == "HIASCDI" else "NA",
				"Agent": entity if entityType == "Agent" else "NA",
				"Application": entity if entityType == "Application" else "NA",
				"Device": entity if entityType == "Device" else "NA",
				"Staff": entity if entityType == "Staff" else "NA",
				"Status": status,
				"Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			})

			if _id != False:
				self.helpers.logger.info(
					entityType + " " + entity + " status update OK")

				self.mqtt.publish("Integrity", {
					"_id": str(_id),
					"Status": status
				})

			else:
				self.helpers.logger.error(
				entityType + " " + entity + " status update KO")

		else:
			self.helpers.logger.error(
				entityType + " " + entity + " status update KO")

	def lifeCallback(self, topic, payload):
		"""Called in the event of a life payload

		Args:
			topic (str): The topic the payload was sent to.
			payload (:obj:`str`): The payload.
		"""

		data = json.loads(payload.decode("utf-8"))
		splitTopic = topic.split("/")

		if splitTopic[1] not in self.ignoreTypes:
			entityType = splitTopic[1][:-1]
		else:
			entityType = splitTopic[1]

		if entityType in ["Robotics", "Application", "Staff"]:
			entity = splitTopic[2]
		else:
			entity = splitTopic[3]

		self.helpers.logger.info(
			"Received " + entityType  + " Life")

		attrs = self.getRequiredAttributes(entityType, entity)
		bch = attrs["blockchain"]

		if not self.hiasbch.iotJumpWayAccessCheck(bch):
			return

		entity = attrs["id"]
		location = attrs["location"]
		zone = attrs["zone"] if "zone" in attrs else "NA"

		updateResponse = self.hiascdi.updateEntity(
			entity, entityType, {
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

		if updateResponse:
			_id = self.hiashdi.insertData("Life", {
				"Use": entityType,
				"Location": location,
				"Zone": zone,
				"HIASCDI": entity if entityType == "HIASCDI" else "NA",
				"Agent": entity if entityType == "Agent" else "NA",
				"Application": entity if entityType == "Application" else "NA",
				"Device": entity if entityType == "Device" else "NA",
				"Staff": entity if entityType == "Staff" else "NA",
				"Data": data,
				"Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			})

			if _id != False:
				self.helpers.logger.info(
					entityType + " " + entity + " life update OK")

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
				entityType + " " + entity + " life update KO")
		else:
			self.helpers.logger.error(
				entityType + " " + entity + " life update KO")

	def sensorsCallback(self, topic, payload):
		"""Called in the event of a sensor payload

		Args:
			topic (str): The topic the payload was sent to.
			payload (:obj:`str`): The payload.
		"""

		data = json.loads(payload.decode("utf-8"))
		splitTopic = topic.split("/")

		if splitTopic[1] not in self.ignoreTypes:
			entityType = splitTopic[1][:-1]
		else:
			entityType = splitTopic[1]

		if entityType in ["Robotics", "Application", "Staff"]:
			entity = splitTopic[2]
		else:
			entity = splitTopic[3]

		self.helpers.logger.info(
			"Received " + entityType  + " Sensors Data")

		attrs = self.getRequiredAttributes(entityType, entity)
		bch = attrs["blockchain"]

		if not self.hiasbch.iotJumpWayAccessCheck(bch):
			return

		entity = attrs["id"]
		location = attrs["location"]
		zone = attrs["zone"] if "zone" in attrs else "NA"

		sensors = self.hiascdi.getSensors(
			entity, entityType)
		sensorData = sensors["sensors"]

		i = 0
		for sensor in sensorData["value"]:
			for prop in sensor["properties"]["value"]:
				if data["Type"].lower() in prop:
					sensorData["value"][i]["properties"]["value"][data["Type"].lower()] = {
						"value": data["Value"],
						"timestamp":  {
							"value": datetime.now().isoformat()
						}
					}
			i = i + 1

		updateResponse = self.hiascdi.updateEntity(
			entity, entityType, {
				"networkStatus": {"value": "ONLINE"},
				"networkStatus.metadata": {"timestamp":  {
					"value": datetime.now().isoformat()
				}},
				"dateModified": {"value": datetime.now().isoformat()},
				"sensors": sensorData
			})

		if updateResponse:
			_id = self.hiashdi.insertData("Sensors", {
				"Use": entityType,
				"Location": location,
				"Zone": zone,
				"Device": entity if entityType == "Device" else "NA",
				"HIASCDI": entity if entityType == "HIASCDI" else "NA",
				"Agent": entity if entityType == "Agent" else "NA",
				"Application": entity if entityType == "Application" else "NA",
				"Device": entity if entityType == "Device" else "NA",
				"Staff": entity if entityType == "Staff" else "NA",
				"Sensor": data["Sensor"],
				"Type": data["Type"],
				"Value": data["Value"],
				"Message": data["Message"],
				"Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			})

			if _id != False:
				self.helpers.logger.info(
					entityType + " " + entity + " sensors update OK")

				self.mqtt.publish("Integrity", {
					"_id": str(_id),
					"Sensor": data["Sensor"],
					"Type": data["Type"],
					"Value": data["Value"],
					"Message": data["Message"]
				})

			else:
				self.helpers.logger.error(
				entityType + " " + entity + " sensors update KO")
		else:
			self.helpers.logger.error(
				entityType + " " + entity + " sensors update KO")

	def actuatorCallback(self, topic, payload):
		"""Called in the event of a actuator payload

		Args:
			topic (str): The topic the payload was sent to.
			payload (:obj:`str`): The payload.
		"""

		data = json.loads(payload.decode("utf-8"))
		splitTopic = topic.split("/")

		if splitTopic[1] not in self.ignoreTypes:
			entityType = splitTopic[1][:-1]
		else:
			entityType = splitTopic[1]

		if entityType in ["Robotics", "Application", "Staff"]:
			entity = splitTopic[2]
		else:
			entity = splitTopic[3]

		self.helpers.logger.info(
			"Received " + entityType  + " Actuators Data")

		attrs = self.getRequiredAttributes(entityType, entity)
		bch = attrs["blockchain"]

		if not self.hiasbch.iotJumpWayAccessCheck(bch):
			return

		entity = attrs["id"]
		location = attrs["location"]
		zone = attrs["zone"] if "zone" in attrs else "NA"

		actuators = self.hiascdi.getActuators(
			entity, entityType)
		actuatorData = actuators["actuators"]

		i = 0
		for actuator in actuatorData["value"]:
			commandExists = True
			if data["Name"] in actuator["name"]["value"] and data["Type"].lower() in actuator["commands"]["value"] \
				and data["Value"].lower() in actuator["commands"]["value"][data["Type"].lower()]:
				actuatorData["value"][i]["state"] = {
					"value": data["Value"],
					"metadata":{
						"timestamp": {
							"value": datetime.now().isoformat()
						}
					}
				}
			i = i + 1

		if commandExists:
			updateResponse = self.hiascdi.updateEntity(
			entity, entityType, {
				"networkStatus": {"value": "ONLINE"},
				"networkStatus.metadata": {"timestamp":  {
					"value": datetime.now().isoformat()
				}},
				"dateModified": {"value": datetime.now().isoformat()},
				"actuators": actuatorData
			})

			if updateResponse:
				_id = self.hiashdi.insertData("Actuators", {
					"Use": entityType,
					"Location": location,
					"Zone": zone,
					"Device": entity if entityType == "Device" else "NA",
					"HIASCDI": entity if entityType == "HIASCDI" else "NA",
					"Agent": entity if entityType == "Agent" else "NA",
					"Application": entity if entityType == "Application" else "NA",
					"Device": entity if entityType == "Device" else "NA",
					"Staff": entity if entityType == "Staff" else "NA",
					"Actuator": data["Name"],
					"Type": data["Type"],
					"Value": data["Value"],
					"Message": data["Message"],
					"Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				})

				if _id != False:
					self.helpers.logger.info(
						entityType + " " + entity + " actuators update OK")

					self.mqtt.publish("Integrity", {
						"_id": str(_id),
						"Actuator": data["Name"],
						"Type": data["Type"],
						"Value": data["Value"],
						"Message": data["Message"]
					})

				else:
					self.helpers.logger.error(
					entityType + " " + entity + " actuators update KO")
			else:
				self.helpers.logger.error(
					entityType + " " + entity + " actuators update KO")

	def respond(self, responseCode, response):
		""" Returns the request repsonse """

		return Response(response=json.dumps(response, indent=4), status=responseCode,
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

	agent.hiascdiConn()
	agent.hiashdiConn()
	agent.hiasbchConn()
	agent.mqttConn({
		"host": agent.credentials["iotJumpWay"]["host"],
		"port": agent.credentials["iotJumpWay"]["port"],
		"location": agent.credentials["iotJumpWay"]["location"],
		"zone": agent.credentials["iotJumpWay"]["zone"],
		"entity": agent.credentials["iotJumpWay"]["entity"],
		"name": agent.credentials["iotJumpWay"]["name"],
		"un": agent.credentials["iotJumpWay"]["un"],
		"up": agent.credentials["iotJumpWay"]["up"]
	})

	agent.mqtt.statusCallback = agent.statusCallback
	agent.mqtt.lifeCallback = agent.lifeCallback
	agent.mqtt.sensorsCallback = agent.sensorsCallback
	agent.mqtt.actuatorCallback = agent.actuatorCallback

	agent.threading()

	app.run(host=agent.helpers.credentials["server"]["ip"],
			port=agent.helpers.credentials["server"]["port"])

if __name__ == "__main__":
	main()

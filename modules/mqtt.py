#!/usr/bin/env python3
""" HIAS iotJumpWay MQTT Module

This module connects devices, applications, robots and software to the HIAS
iotJumpWay MQTT Broker.

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

import paho.mqtt.client as pmqtt

class mqtt():
    """HIAS iotJumpWay MQTT Module

    This module connects devices, applications, robots and software to
    the HIAS iotJumpWay MQTT Broker.
    """

    def __init__(self,
                 helpers,
                 client_type,
                 configs):
        """ Initializes the class. """

        self.configs = configs
        self.client_type = client_type
        self.is_connected = False

        self.helpers = helpers
        self.program = "HIAS iotJumpWay MQTT Module"

        self.mqtt_config = {}
        self.module_topics = {}

        self.agent = [
            'host',
            'port',
            'location',
            'zone',
            'entity',
            'name',
            'un',
            'up'
        ]

        self.helpers.logger.info(
            self.program + " initialization complete.")

    def configure(self):
        """ Connection configuration.

        Configures the HIAS iotJumpWay MQTT connnection.
        """

        self.client_id = self.configs['name']
        for param in self.agent:
            if self.configs[param] is None:
                raise ConfigurationException(
                    param + " parameter is required!")

        # Sets MQTT connection configuration
        self.mqtt_config["host"] = self.configs['host']
        self.mqtt_config["port"] = self.configs['port']
        self.mqtt_config["security"] = self.configs['security']
        if self.mqtt_config["security"]:
            self.mqtt_config["tls"] = "/etc/ssl/certs/ISRG_Root_X1.pem"

        # Sets MQTT topics
        self.module_topics["statusTopic"] = '%s/Agents/%s/%s/Status' % (
            self.configs['location'], self.configs['zone'], self.configs['entity'])

        # Sets MQTT callbacks
        self.actuators_callback = None
        self.ai_model_callback = None
        self.ai_agent_callback = None
        self.bci_callback = None
        self.classification_callback = None
        self.comands_callback = None
        self.integrityCallback = None
        self.life_callback = None
        self.notifications_callback = None
        self.sensors_callback = None
        self.state_callback = None
        self.status_callback = None
        self.zoneCallback = None

        self.helpers.logger.info(
            "iotJumpWay " + self.client_type + " connection configured.")

    def start(self):
        """ Connection

        Starts the HIAS iotJumpWay MQTT connection.
        """

        self.m_client = pmqtt.Client(
            client_id=self.client_id, clean_session=True)
        
        self.m_client.will_set(
            self.module_topics["statusTopic"], "OFFLINE", 0, False)
        
        if self.mqtt_config["security"]:
            self.m_client.tls_set(
                self.mqtt_config["tls"], certfile=None, keyfile=None)
            
        self.m_client.on_connect = self.on_connect
        self.m_client.on_message = self.on_message
        self.m_client.on_publish = self.on_publish
        self.m_client.on_subscribe = self.on_subscribe
        self.m_client.on_disconnect = self.on_disconnect
        
        self.m_client.username_pw_set(
            str(self.configs['un']), str(self.configs['up']))
        
        self.m_client.connect(
            self.mqtt_config["host"], self.mqtt_config["port"], 10)
        
        self.m_client.loop_start()

        self.helpers.logger.info(
            "iotJumpWay " + self.client_type + " connection started.")

    def on_connect(self, client, obj, flags, rc):
        """ On connection

        On connection callback.
        """

        if self.is_connected != True:
            self.is_connected = True
            
            self.helpers.logger.info(
                "iotJumpWay " + self.client_type + " connection successful.")
            
            self.helpers.logger.info(
                "rc: " + str(rc))
            
            self.status_publish("ONLINE")
            self.subscribe()

    def on_disconnect(self, client, userdata, rc):
        """ On connection

        On connection callback.
        """

        self.helpers.logger.info(
            "iotJumpWay " + self.client_type + " disconnected.")

        print(userdata)
        print(rc)

    def status_publish(self, data):
        """ Status publish

        Publishes a status.
        """

        self.m_client.publish(
            self.module_topics["statusTopic"], data)
        
        self.helpers.logger.info(
            "Published to " + self.client_type + " status.")

    def on_subscribe(self, client, obj, mid, granted_qos):
        """ On subscribe

        On subscription callback.
        """

        self.helpers.logger.info(
            "iotJumpWay " + self.client_type + " subscription")

    def on_message(self, client, obj, msg):
        """ On message

        On message callback.
        """

        split_topic = msg.topic.split("/")
        conn_type = split_topic[1]

        if conn_type == "Agents":
            topic = split_topic[4]
        elif conn_type == "AiModels":
            topic = split_topic[4]
        elif conn_type == "AiAgents":
            topic = split_topic[4]
        elif conn_type == "Applications":
            topic = split_topic[3]
        elif conn_type == "Devices":
            topic = split_topic[4]
        elif conn_type == "HIASBCH":
            topic = split_topic[4]
        elif conn_type == "HIASCDI":
            topic = split_topic[4]
        elif conn_type == "HIASHDI":
            topic = split_topic[4]
        elif conn_type == "Robotics":
            topic = split_topic[3]
        elif conn_type == "Staff":
            topic = split_topic[3]

        self.helpers.logger.info(msg.payload)
        self.helpers.logger.info(
            "iotJumpWay " + conn_type + " " + msg.topic  + " communication received.")

        if topic == 'Actuators':
            if self.actuators_callback == None:
                self.helpers.logger.info(
                    conn_type + " actuators callback required (actuators_callback)!")
            else:
                self.actuator_state_callback(msg.topic, msg.payload)
        elif topic == 'AiAgent':
            if self.ai_agent_callback == None:
                self.helpers.logger.info(
                    conn_type + " AI Agent callback required (ai_agent_callback)!")
            else:
                self.ai_agent_callback(msg.topic, msg.payload)
        elif topic == 'AiModel':
            if self.ai_model_callback == None:
                self.helpers.logger.info(
                    conn_type + " AI Model callback required (ai_model_callback)!")
            else:
                self.ai_model_callback(msg.topic, msg.payload)
        elif topic == 'BCI':
            if self.bci_callback == None:
                self.helpers.logger.info(
                    conn_type + " BCI callback required (bci_callback)!")
            else:
                self.bci_callback(msg.topic, msg.payload)
        elif topic == 'Classification':
            if self.classification_callback == None:
                self.helpers.logger.info(
                    conn_type + " classification callback required (classification_callback)!")
            else:
                self.classification_callback(msg.topic, msg.payload)
        elif topic == 'Commands':
            if self.comands_callback == None:
                self.helpers.logger.info(
                    conn_type + " comands callback required (comands_callback)!")
            else:
                self.comands_callback(msg.topic, msg.payload)
        elif topic == 'Integrity':
            if self.integrityCallback == None:
                self.helpers.logger.info(
                    conn_type + " Integrity callback required (integrityCallback)!")
            else:
                self.integrityCallback(msg.topic, msg.payload)
        elif topic == 'Life':
            if self.life_callback == None:
                self.helpers.logger.info(
                    conn_type + " life callback required (life_callback)!")
            else:
                self.life_callback(msg.topic, msg.payload)
        elif topic == 'Notifications':
            if self.notifications_callback == None:
                self.helpers.logger.info(
                    conn_type + " notifications callback required (notifications_callback)!")
            else:
                self.notifications_callback(msg.topic, msg.payload)
        elif topic == 'Sensors':
            if self.sensors_callback == None:
                self.helpers.logger.info(
                    conn_type + " status callback required (sensors_callback)!")
            else:
                self.sensors_callback(msg.topic, msg.payload)
        elif topic == 'State':
            if self.state_callback == None:
                self.helpers.logger.info(
                    conn_type + " state callback required (state_callback)!")
            else:
                self.state_callback(msg.topic, msg.payload)
        elif topic == 'Status':
            if self.status_callback == None:
                self.helpers.logger.info(
                    conn_type + " status callback required (status_callback)!")
            else:
                self.status_callback(msg.topic, msg.payload)
        elif topic == 'Zone':
            if self.zoneCallback == None:
                self.helpers.logger.info(
                    conn_type + " status callback required (zoneCallback)!")
            else:
                self.zoneCallback(msg.topic, msg.payload)

    def publish(self, channel, data, channel_path = ""):
        """ Publish

        Publishes a iotJumpWay MQTT payload.
        """

        if channel == "Custom":
            channel = channel_path
        else:
            channel = '%s/Agents/%s/%s/%s' % (self.configs['location'],
                self.configs['zone'], self.configs['entity'], channel)

        self.m_client.publish(
            channel, json.dumps(data))
        
        self.helpers.logger.info(
            "Published to " + channel)
        return True

    def subscribe(self, application = None, channelID = None, qos=0):
        """ Subscribe

        Subscribes to an iotJumpWay MQTT channel.
        """

        channel = '%s/#' % (self.configs['location'])
        self.m_client.subscribe(channel, qos=qos)
        
        self.helpers.logger.info(
            "Agent subscribed to all channels")
        return True

    def on_publish(self, client, obj, mid):
        """ On publish

        On publish callback.
        """

        self.helpers.logger.info(
            "Published: "+str(mid))

    def on_log(self, client, obj, level, string):
        """ On log

        On log callback.
        """

        print(string)

    def disconnect(self):
        """ Disconnect

        Disconnects from the HIAS iotJumpWay MQTT Broker.
        """

        self.status_publish("OFFLINE")
        self.m_client.disconnect()
        self.m_client.loop_stop()

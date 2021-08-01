#!/bin/bash

FMSG="- HIAS MQTT IoT Agent service installation terminated"

echo "This script will install the HIAS MQTT IoT Agent service on your device."
read -p "Proceed (y/n)? " proceed

if [ "$proceed" = "Y" -o "$proceed" = "y" ]; then
	echo "- Installing HIAS MQTT IoT Agent service"
	sudo touch /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "[Unit]" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "Description=HIAS MQTT IoT Agent service" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "After=multi-user.target" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "After=HIASCDI.service" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "[Service]" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "User=$USER" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "Type=simple" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "Restart=on-failure" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "ExecStart=/usr/bin/python3 /home/$USER/HIAS/components/agents/mqtt/agent.py" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "[Install]" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "WantedBy=multi-user.target" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service
	echo "" | sudo tee -a /lib/systemd/system/HIAS-MQTT-IoT-Agent.service

	sudo systemctl enable HIAS-MQTT-IoT-Agent.service
	sudo systemctl start HIAS-MQTT-IoT-Agent.service

	echo "- Installed HIAS MQTT IoT Agent service!";
	exit 0
else
	echo $FMSG;
	exit 1
fi
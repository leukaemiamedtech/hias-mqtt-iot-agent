#!/bin/bash

FMSG="- HIAS MQTT IoT Agent installation terminated"

read -p "? This script will install the HIAS MQTT IoT Agent on your device. Are you ready (y/n)? " cmsg

if [ "$cmsg" = "Y" -o "$cmsg" = "y" ]; then
    echo "- Installing HIAS MQTT IoT Agent"
	pip3 install --user flask
	pip3 install --user requests
	pip3 install --user web3
    echo "- HIAS MQTT IoT Agent installed!"
else
    echo $FMSG;
    exit
fi
# Agent Documentation

![HIAS MQTT IoT Agent](img/project-banner.jpg)

[![CURRENT RELEASE](https://img.shields.io/badge/CURRENT%20RELEASE-3.0.0-blue.svg)](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/tree/3.0.0) [![UPCOMING RELEASE](https://img.shields.io/badge/CURRENT%20DEV%20BRANCH-4.0.0-blue.svg)](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/tree/4.0.0) [![Contributions Welcome!](https://img.shields.io/badge/Contributions-Welcome-lightgrey.svg)](CONTRIBUTING.md)  [![Issues](https://img.shields.io/badge/Issues-Welcome-lightgrey.svg)](issues) [![LICENSE](https://img.shields.io/badge/LICENSE-MIT-blue.svg)](LICENSE)

# Introduction

A **HIAS IoT Agent** is a bridge between HIAS network devices and applications, and the HIASCDI Contextual Data Interface. The **HIAS MQTT IoT Agent** is a HIAS AI Agent that communicates with HIAS devices and applications using the MQTT machine to machine communication protocol.

&nbsp;

# MQTT

The Message Queuing Telemetry Transport (MQTT) is a lightweight machine to machine communication protocol designed to provide communication between low resource devices.

The protocol is publish-subscribe (Pub/Sub) communication protocol that runs over the Internet Protocol Suite (TCP/IP).

&nbsp;

# HIAS

![HIAS - Hospital Intelligent Automation Server](img/hias-network.jpg)

[HIAS - Hospital Intelligent Automation Server](https://github.com/AIIAL/HIAS-Core) is an open-source automation server designed to control and manage an intelligent network of IoT connected devices and applications.

## HIAS IoT Agents

The HIAS iotJumpWay Agents are a selection of protocol/transfer specific applications that act as a bridge between the **HIASCDI Contextual Data Interface** & the **HIASHDI Historical Data Interface** and the devices and applications connected to the HIAS network via the iotJumpWay. Supported protocols currently include **HTTP**, **MQTT**, **Websockets**, **AMQP** and **Bluetooth/Bluetooth Low Energy (BLE)**.

Each IoT Agent provides a North & South Port interface that allows communication to and from the Context Broker.

![SOUTHBOUND TRAFFIC (COMMANDS)](img/southbound.jpg)

__Source: [FIWARE IoT Agents](https://fiware-tutorials.readthedocs.io/en/latest/iot-agent/index.html)__

The North Port interface of an IoT Agent listens to southbound traffic coming from the Context Broker towards the devices and applications.

![NORTHBOUND TRAFFIC (MEASUREMENTS)](img/southbound.jpg)

__Source: [FIWARE IoT Agents](https://fiware-tutorials.readthedocs.io/en/latest/iot-agent/index.html)__

The IoT Agent sends southbound traffic to devices and applications using a protocol that is supported by the device/application, and receives northbound traffic from the devices/applications which it then forwards to the Context Broker.

&nbsp;

# GETTING STARTED

To get started, follow the following guides:

- [Ubuntu installation guide](installation/ubuntu.md)
- [Ubuntu usage guide](usage/ubuntu.md)

&nbsp;

# Contributing
Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss encourages and welcomes code contributions, bug fixes and enhancements from the Github community.

Please read the [CONTRIBUTING](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/blob/main/CONTRIBUTING.md "CONTRIBUTING") document for a full guide to forking our repositories and submitting your pull requests. You will also find our code of conduct in the [Code of Conduct](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/blob/main/CODE-OF-CONDUCT.md) document.

## Contributors
- [Adam Milton-Barker](https://www.leukemiaairesearch.com/association/volunteers/adam-milton-barker "Adam Milton-Barker") - [Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss](https://www.leukemiaresearchassociation.ai "Asociación de Investigacion en Inteligencia Artificial Para la Leucemia Peter Moss") President/Founder & Lead Developer, Sabadell, Spain

&nbsp;

# Versioning
We use SemVer for versioning.

&nbsp;

# License
This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/blob/main/LICENSE "LICENSE") file for details.

&nbsp;

# Bugs/Issues
We use the [repo issues](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/issues "repo issues") to track bugs and general requests related to using this project. See [CONTRIBUTING](https://github.com/AIIAL/HIAS-MQTT-IoT-Agent/CONTRIBUTING.md "CONTRIBUTING") for more info on how to submit bugs, feature requests and proposals.
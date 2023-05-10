#  Usage Guide (Ubuntu)

![HIAS MQTT IoT Agent](../img/project-banner.jpg)

# Introduction
This guide will take you through using the **HIAS MQTT IoT Agent**.

&nbsp;

# Prerequisites

- You must have completed the [HIAS MQTT IoT Agent installation guide](../installation/ubuntu.md).

- Ensure **HIAS**, **HIASBCH**, **HIASHDI** and **HIASCDI** are **running**.

&nbsp;

# Start the Agent

Now you are ready to fire up your HIAS MQTT IoT Agent, to do so use the following command:

``` bash
sudo systemctl start HIAS-MQTT-IoT-Agent.service
```

# Manage the Agent

To manage the agent you can use the following commands:

``` bash
sudo systemctl restart HIAS-MQTT-IoT-Agent.service
sudo systemctl stop HIAS-MQTT-IoT-Agent.service
sudo systemctl status HIAS-MQTT-IoT-Agent.service
```

&nbsp;

# Contributing
Peter Moss Leukaemia MedTech Research CIC encourages and welcomes code contributions, bug fixes and enhancements from the Github community.

Please read the [IOT AGENT CONTRIBUTING](https://github.com/leukaemiamedtech/contributing-guides/blob/main/CONTRIBUTING-GUIDE-IOT-AGENTS.md "IOT AGENT CONTRIBUTING") guide for a full guide to contributing to our IoT Agent projects. You will also find our code of conduct in the [CODE OF CONDUCT](https://github.com/leukaemiamedtech/contributing-guides/blob/main/CODE-OF-CONDUCT.md) document.

## Contributors
- [Adam Milton-Barker](https://www.leukaemiamedtechresearch.org.uk/about/volunteers/adam-milton-barker "Adam Milton-Barker") - [Peter Moss Leukaemia MedTech Research CIC](https://www.leukaemiamedtechresearch.org.uk "Peter Moss Leukaemia MedTech Research CIC") Founder & Managing Director.

&nbsp;

# Versioning
We use [SemVer](https://semver.org/) for versioning.

&nbsp;

# License
This project is licensed under the **MIT License** - see the [LICENSE](LICENSE "LICENSE") file for details.

&nbsp;

# Bugs/Issues
We use the [repo issues](https://github.com/leukaemiamedtech/hias-mqtt-iot-agent/issues/new/choose "repo issues") to track bugs and general requests related to using this project. See [IOT AGENT CONTRIBUTING](https://github.com/leukaemiamedtech/contributing-guides/blob/main/CONTRIBUTING-GUIDE-IOT-AGENTS.md "IOT AGENT CONTRIBUTING") guide for more info on how to submit bugs, feature requests and proposals.
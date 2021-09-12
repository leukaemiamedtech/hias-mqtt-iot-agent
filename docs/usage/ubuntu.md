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
```

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
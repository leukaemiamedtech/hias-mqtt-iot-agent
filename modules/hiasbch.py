#!/usr/bin/env python3
""" HIASBCH Helper Module

This module provides helper functions that allow the HIAS IoT Agents
to communicate with the HIASBCH Blockchain.

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
import sys
import time

from requests.auth import HTTPBasicAuth
from web3 import Web3


class hiasbch():
    """ HIASBCH Helper Module

    This module provides helper functions that allow the HIAS IoT
    Agents to communicate with the HIASBCH Blockchain.
    """

    def __init__(self, helpers):
        """ Initializes the class. """

        self.helpers = helpers
        self.confs = self.helpers.confs
        self.credentials = self.helpers.credentials

        self.helpers.logger.info("HIASBCH Class initialization complete.")

    def start(self):
        """ Connects to HIASBCH. """

        self.w3 = Web3(Web3.HTTPProvider(
            "http://" + self.credentials["server"]["host"] + self.credentials["hiasbch"]["endpoint"], request_kwargs={
                        'auth': HTTPBasicAuth(self.credentials["iotJumpWay"]["entity"],
                                              self.confs["agent"]["proxy"]["up"])}))
        self.iotContract = self.w3.eth.contract(
            self.w3.toChecksumAddress(self.credentials["hiasbch"]["contracts"]["iotJumpWay"]["contract"]),
            abi=json.dumps(self.credentials["hiasbch"]["contracts"]["iotJumpWay"]["abi"]))
        self.helpers.logger.info("HIASBCH connections started")

    def iotjumpway_access_check(self, address):
        """ Checks sender is allowed access to the iotJumpWay Smart Contract """

        self.helpers.logger.info("HIASBCH checking " + address)
        if not self.iotContract.functions.accessAllowed(
                    self.w3.toChecksumAddress(address)).call({
                        'from': self.w3.toChecksumAddress(self.credentials["hiasbch"]["un"])}):
            return False
        else:
            return True


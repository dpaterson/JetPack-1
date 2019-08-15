#!/usr/bin/python

# Copyright (c) 2016-2019 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import argparse
from collections import defaultdict
from collections import namedtuple
from constants import Constants
from shutil import copyfile
import json
import logging
import math
import os
import sys
import yaml
import errno
import fcntl
import time

from dracclient import utils
from dracclient.constants import POWER_OFF
from dracclient.constants import POWER_ON
from dracclient.constants import REBOOT
from dracclient.constants import RebootRequired
from dracclient.exceptions import DRACOperationFailed, \
    DRACUnexpectedReturnValue, WSManInvalidResponse, WSManRequestFailure
from oslo_utils import units
from arg_helper import ArgHelper
from credential_helper import CredentialHelper
from ironic_helper import IronicHelper
from job_helper import JobHelper
from logging_helper import LoggingHelper
import requests.packages
from ironicclient.common.apiclient.exceptions import InternalServerError

discover_nodes_path = os.path.join(os.path.expanduser('~'),
                                   'pilot/discover_nodes')

sys.path.append(discover_nodes_path)

from discover_nodes.dracclient.client import DRACClient  # noqa
requests.packages.urllib3.disable_warnings()

logging.basicConfig()

LOG = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])

STATES = {
    'on': POWER_ON,
    'off': POWER_OFF,
    'reboot': REBOOT
}


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Assigns role to Overcloud node.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("ip_mac_service_tag",
                        help="""IP address of the iDRAC, MAC address of the
                                interface on the provisioning network,
                                or service tag of the node""",
                        metavar="ADDRESS")
    parser.add_argument("state",
                        type=state_index,
                        help="""set node state, on, off, reboot""",
                        metavar="STATE")

    ArgHelper.add_instack_arg(parser)

    LoggingHelper.add_argument(parser)

    return parser.parse_args()


def state_index(state):

    if state not in STATES.keys():
        raise argparse.ArgumentTypeError(
            "{} is not a valid state; choices are {}".format(
                state, str(
                    STATES.keys())))

    return STATES[state]


def get_drac_client(node_definition_filename, node):
    drac_ip, drac_user, drac_password = \
        CredentialHelper.get_drac_creds_from_node(node,
                                                  node_definition_filename)
    drac_client = DRACClient(drac_ip, drac_user, drac_password)

    return drac_client


def set_powered_state(drac_client, state):
     current_state = drac_client.get_power_state()
     if ((state is POWER_OFF 
        and current_state is not POWER_OFF)
        or (state is POWER_ON and current_state is not POWER_ON)
        or (state is REBOOT and current_state is POWER_ON)):
        LOG.info("Setting power state to: {}".format(state))
        drac_client.set_power_state(state)
     else:
         LOG.error("Invalid power state selected: {}, node is most " 
                   "likely already in desired power state".format(state))


def main():

    drac_client = None

    args = parse_arguments()

    LoggingHelper.configure_logging(args.logging_level)

    ironic_client = IronicHelper.get_ironic_client()

    node = IronicHelper.get_ironic_node(ironic_client,
                                            args.ip_mac_service_tag)
    if node is None:
        LOG.critical("Unable to find node {}".format(
                     args.ip_mac_service_tag))
        sys.exit(1)

    drac_client = get_drac_client(args.node_definition, node)

    if drac_client is not None:
        LOG.info("Setting node state to: {}".format(args.state))
        set_powered_state(drac_client, args.state)


if __name__ == "__main__":
    main()

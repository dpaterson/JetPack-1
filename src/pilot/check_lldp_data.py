
#!/usr/bin/python

# Copyright (c) 2017-2020 Dell Inc. or its subsidiaries.
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

import argparse
import logging
import os
import sys
import subprocess
from arg_helper import ArgHelper
from job_helper import JobHelper
from logging_helper import LoggingHelper
from time import sleep
from utils import Utils
from lldp_helper import LLDPHelper

LOG = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])

NOT_SUPPORTED_MSG = " operation is not supported on th"

ROLES = {
    'controller': 'control',
    'compute': 'compute',
    'storage': 'ceph-storage',
    'computehci': 'computehci'
}

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Validate LLDP data collected for the given node/role.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--ip_mac_service_tag",
                        help="""IP address of the iDRAC, MAC address of the
                                    interface on the provisioning network,
                                    or service tag of the node""",
                        metavar="ADDRESS")
    parser.add_argument("--role",
                        help="""role that the node will play, with an optional
                                    index that indicates placement order in the
                                    rack; choices are controller[-<index>],
                                    compute[-<index>], and storage[-<index>]""",
                        metavar="ROLE")
    parser.add_argument("--nic-template",
                        help="file that contains flavor settings",
                        metavar="FILENAME")
    ArgHelper.add_instack_arg(parser)

    LoggingHelper.add_argument(parser)

    return parser.parse_args()

def get_nic_template(nic_filename):
    #
    nic_template = None
    try:
        with open(nic_filename, 'r') as f:
            nic_template = f.readlines()

    except IOError:
        LOG.exception(
            "Could not open nic template file {}".format(nic_filename))

    return nic_template

def Validate_LLDP(ip_service_tag, nic_template, role):
    #
    helper = LLDPHelper()
    template = get_nic_template(nic_template)
    errors = []
    for each in template:
        if role.lower() in each.lower():
            if "Interface" in each:
                if "mode" in each:
                    pass
                else:
                    interface = each.split(":")[1].strip()
                    print ("Checking " + str(interface))
                    status = helper.verify_interface_connected(ip_service_tag, interface)
                    if status is False:
                        errors.append(interface)
    if len(errors) > 0:
        LOG.exception("Some interfaces were not connected  {}: "
                      "{}".format(ip_service_tag, str(errors)))



def main():

    args = parse_arguments()
    print(" > " + str(args))
    LoggingHelper.configure_logging(args.logging_level)

    try:

        # args.ip_service_tag
        # Role

        Validate_LLDP(args.ip_mac_service_tag,
                     args.nic_template,
                     args.role)
    except ValueError as ex:
        LOG.error("An error occurred while Validating LLDP data for node {}: {}".format(
            args.ip_mac_service_tag, ex.message))
        sys.exit(1)
    except Exception as ex:
        LOG.exception("An error occurred while Validating LLDP data for node {}: "
                      "{}".format(args.ip_mac_service_tag, ex.message))
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig()
    main()
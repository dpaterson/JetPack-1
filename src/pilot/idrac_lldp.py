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
import requests.packages
import sys

from arg_helper import ArgHelper
from dracclient import client
from dracclient import wsman
from dracclient import exceptions
from dracclient.resources import uris
from dracclient.resources import nic
import boot_mode_helper
from boot_mode_helper import BootModeHelper
from constants import Constants
from credential_helper import CredentialHelper
from job_helper import JobHelper
from logging_helper import LoggingHelper
from time import sleep
from utils import Utils

# Suppress InsecureRequestWarning: Unverified HTTPS request is being made
requests.packages.urllib3.disable_warnings()

LOG = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Performs initial configuration of an iDRAC.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    ArgHelper.add_ip_service_tag(parser)

    parser.add_argument("-u",
                        "--user",
                        help="""username""",
                        metavar="user")
    parser.add_argument("-p",
                        "--password",
                        help="Password",
                        metavar="password")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e",
                       "--enable",
                       action='store_true',
                       help="Enable LLDP attributes on iDRAC")
    group.add_argument("-d",
                       "--disable",
                       action='store_true',
                       help="Disable LLDP attributes on iDRAC")

    LoggingHelper.add_argument(parser)

    return parser.parse_args()



def main():
    """
    <ns34:DCIM_iDRACCardEnumeration xmlns:ns34="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardEnumeration">
      <ns34:AttributeDisplayName>Enable</ns34:AttributeDisplayName>
      <ns34:AttributeName>Enable</ns34:AttributeName>
      <ns34:CurrentValue>Enabled</ns34:CurrentValue>
      <ns34:DefaultValue>Enabled</ns34:DefaultValue>
      <ns34:Dependency xsi:nil="true"/>
      <ns34:DisplayOrder>1</ns34:DisplayOrder>
      <ns34:FQDD>iDRAC.Embedded.1</ns34:FQDD>
      <ns34:GroupDisplayName>Switch Connection View</ns34:GroupDisplayName>
      <ns34:GroupID>SwitchConnectionView.1</ns34:GroupID>
      <ns34:InstanceID>iDRAC.Embedded.1#SwitchConnectionView.1#Enable</ns34:InstanceID>
      <ns34:IsReadOnly>false</ns34:IsReadOnly>
      <ns34:PendingValue xsi:nil="true"/>
      <ns34:PossibleValues>Disabled</ns34:PossibleValues>
      <ns34:PossibleValues>Enabled</ns34:PossibleValues>
    </ns34:DCIM_iDRACCardEnumeration>
    <ns310:DCIM_iDRACCardEnumeration xmlns:ns310="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardEnumeration">
      <ns310:AttributeDisplayName>Discovery LLDP</ns310:AttributeDisplayName>
      <ns310:AttributeName>DiscoveryLLDP</ns310:AttributeName>
      <ns310:CurrentValue>Enabled</ns310:CurrentValue>
      <ns310:DefaultValue>Disabled</ns310:DefaultValue>
      <ns310:Dependency xsi:nil="true"/>
      <ns310:DisplayOrder>119</ns310:DisplayOrder>
      <ns310:FQDD>iDRAC.Embedded.1</ns310:FQDD>
      <ns310:GroupDisplayName>NIC Information</ns310:GroupDisplayName>
      <ns310:GroupID>NIC.1</ns310:GroupID>
      <ns310:InstanceID>iDRAC.Embedded.1#NIC.1#DiscoveryLLDP</ns310:InstanceID>
      <ns310:IsReadOnly>false</ns310:IsReadOnly>
      <ns310:PendingValue xsi:nil="true"/>
      <ns310:PossibleValues>Disabled</ns310:PossibleValues>
      <ns310:PossibleValues>Dedicated</ns310:PossibleValues>
      <ns310:PossibleValues>SharedLOM</ns310:PossibleValues>
      <ns310:PossibleValues>Enabled</ns310:PossibleValues>
    </ns310:DCIM_iDRACCardEnumeration>
    <ns316:DCIM_iDRACCardEnumeration xmlns:ns316="http://schemas.dell.com/wbem/wscim/1/cim-schema/2/DCIM_iDRACCardEnumeration">
      <ns316:AttributeDisplayName>TopologyLLDP</ns316:AttributeDisplayName>
      <ns316:AttributeName>TopologyLldp</ns316:AttributeName>
      <ns316:CurrentValue>Enabled</ns316:CurrentValue>
      <ns316:DefaultValue>Disabled</ns316:DefaultValue>
      <ns316:Dependency xsi:nil="true"/>
      <ns316:DisplayOrder>105</ns316:DisplayOrder>
      <ns316:FQDD>iDRAC.Embedded.1</ns316:FQDD>
      <ns316:GroupDisplayName>NIC Information</ns316:GroupDisplayName>
      <ns316:GroupID>NIC.1</ns316:GroupID>
      <ns316:InstanceID>iDRAC.Embedded.1#NIC.1#TopologyLldp</ns316:InstanceID>
      <ns316:IsReadOnly>false</ns316:IsReadOnly>
      <ns316:PendingValue xsi:nil="true"/>
      <ns316:PossibleValues>Disabled</ns316:PossibleValues>
      <ns316:PossibleValues>Enabled</ns316:PossibleValues>
    </ns316:DCIM_iDRACCardEnumeration>

    result = self.drac_client.set_idrac_settings(
        {'LDAP.1#GroupAttributeIsDN': 'Disabled'})

    self.assertEqual({'is_commit_required': True,
                      'is_reboot_required':
                          constants.RebootRequired.false},
                     result)
    """
    args = parse_arguments()

    LoggingHelper.configure_logging(args.logging_level)
    LOG.info(args)
    desired_state = "Enabled" if args.enable else "Disabled"
    lldp_attrs = {}
    """ Below turns off idrac settings -> overview -> network settings
    -> common -> Connection View.
    it is enabled by default so leaving out for now. After reading below
    I don't think this bit has anything to do with lldp, it just let's you
    see what the idrac switch connection info.
    From: Dell_iDRACCard_Profile.pdf
    7.5.56. SwitchConnectionView
        This section describes the attributes for
        Switch Connection View feature.

        The GroupID property for the DCIM_iDRACCardEnumeration shall be
        “SwitchConnectionView.1” and for DCIM_iDRACCardString shell be NIC.1
        The GroupDisplayName property for the DCIM_iDRACCardEnumeration
        shall be“Switch Connection View” and DCIM iDRACCardString shell be NIC
        Information.
        The following table describes the values for the
        DCIM_iDRACCardEnumeration and DCIM_iDRACCardString of this group.
        Each column heading corresponds to a property name on the
        DCIM_iDRACCardEnumeration and DCIM_iDRACCardString class.
        The Description column contains the description for each of the
        attribute. Each row contains the values for the properties listed in
        the column headings. The PossibleValues property is an array property
        represented in the table as comma delimited list.
        “SetAttribute/SetAttributes/ApplyAttribute/ ApplyAttributes” methods
        in DCIM_ iDRAC CardService will be used to modify the
        DCIM_iDRACCardEnumeration Attributes.
        Table 116. DCIM_iDRACCardEnumeration SwitchConnectionView
        AttributeName: Enable
        AttributeDisplayName: Enable
        IsReadOnly: FALSE
        PossibleValues:
        0 – “Disabled”
        1 – “Enabled”
    lldp_attrs['SwitchConnectionView.1#Enable']  = desired_state
    """
    lldp_attrs['NIC.1#DiscoveryLLDP'] = desired_state
    lldp_attrs['NIC.1#TopologyLldp'] = desired_state

    try:
        drac_client = client.DRACClient(args.ip_service_tag,
                                        args.user, args.password)

        LOG.info('{} lldp  iDRAC attributes: '
                 '{} on {}'.format(desired_state, str(lldp_attrs),
                                   args.ip_service_tag))
        res = drac_client.set_idrac_settings(lldp_attrs)
        LOG.info('Results: {}'.format(str(res)))
        id = drac_client.commit_pending_idrac_changes()
        LOG.info('Config job ID: {}'.format(str(id)))

    except Exception as ex:
        LOG.exception("An error occurred while configuring iDRAC {}: "
                      "{}".format(args.ip_service_tag, ex.message))
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig()
    main()

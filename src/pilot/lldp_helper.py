#!/usr/bin/env python

# Copyright (c) 2020 Dell Inc. or its subsidiaries.
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


import os, sys, subprocess
from ironic_helper import IronicHelper
from subprocess import check_output

class LLDPHelper():

    def __init__(self):
         self.ironic_client = IronicHelper.get_ironic_client()

    def get_node_uuid(self,idrac_ip):
        return IronicHelper.get_ironic_node(self.ironic_client, idrac_ip).uuid
    
    def get_node_basic_lldp_data(self, idrac_ip):
        uuid = self.get_node_uuid(idrac_ip)
        cmd = "source ~/stackrc;openstack baremetal introspection interface list " + str(uuid)
        ret = subprocess.check_output(cmd, stderr=subprocess.STDOUT,shell=True).decode("utf-8")
        interfaces= []
        tab = ret.split("\n")
        ls = tab[3:]
        for interface in ls:
            #print(interface)
            info = interface.split('|')
            if len(info) < 2:
                pass
            else:
                inter = type('lldp_data', (object,), {})()
                inter.interface = info[1].strip()
                inter.mac = info[2].strip()
                inter.swith_chasis = info[4].strip()
                inter.switch_port = info[5].strip()
                interfaces.append(inter)

        return interfaces

    def get_connected_interfaces(self, idrac_ip):
        lldp_data = self.get_node_basic_lldp_data(idrac_ip)
        connected = []
        for each in lldp_data:
            #print("." +  str(each.interface) + " :: " + str(each.swith_chasis))
            if "None" in each.switch_port :
                pass
                #print (each.interface + " present but not connected to switch")
            else:
                #print(" > "  + str(each.switch_port))
                connected.append(each.interface)
        return connected

    def verify_interface_connected(self,idrac_ip, interface):
        connected = self.get_connected_interfaces(idrac_ip)
        if interface in connected:
            print("Found Connected interface : " + str(interface) + " to " + self.get_interface_switch_chasis(idrac_ip, interface))
            return True
        else:
            print( interface + " NOT present/Connected")
            return False


    def get_interface_switch_chasis(self, idrac_ip, interface):
        data = self.get_node_basic_lldp_data(idrac_ip)
        for each in data:
            if each.interface == interface:
                return each.swith_chasis
        print (interface + " NOT FOUND")
    
    def verify_interfaces_do_not_share_switch(self,idrac_ip, interface1, interface2):
        a = self.get_interface_switch_chasis(idrac_ip, interface1)
        b = self.get_interface_switch_chasis(idrac_ip, interface2)
        if a == b:
            print ("Interfaces share the same switch " + str(a))
        else :
            print ("Interfaces use different switches " + str(a) + " >< " + str(b))

#!/usr/bin/env python

# Copyright (c) 2015-2020 Dell Inc. or its subsidiaries.
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


class NodeConf():

    def __init__(self, json):
        self.is_sah = False
        self.is_foreman = False
        self.is_dashboard = False
        self.is_director = False
        self.is_ceph_storage = False
        self.is_controller = False
        self.is_compute = False
        self.is_computehci = False
        self.is_switch = False
        self.hostname = None
        self.idrac_ip = None
        self.service_tag = None
        self.root_password = None
        self.anaconda_ip = None
        self.anaconda_iface = None
        self.external_ip = None
        self.management_ip = None
        self.private_api_ip = None
        self.public_api_gateway = None
        self.public_bond = None
        self.public_api_ip = None
        self.external_ip = None
        self.external_netmask = None
        self.public_slaves = None
        self.provisioning_ip = None
        self.provisioning_gateway = None
        self.provisioning_bond = None
        self.provisioning_netmask = None
        self.provisioning_slaves = None
        self.storage_ip = None
        self.storage_cluster_ip = None
        self.tenant_tunnel_ip = None
        self.name_server = None
        self.skip_raid_config = False
        self.skip_bios_config = False
        self.skip_nic_config = False
        self.skip_idrac_config = False
        self.__dict__ = json

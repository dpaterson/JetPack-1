#!/bin/bash
# Copy modified templates and python code 
# needed to implement DCN
echo "Copying templates for DCN"
cp ~/JetPack-1/src/pilot/templates/network-environment.yaml ~/pilot/templates/
cp ~/JetPack-1/src/pilot/templates/network-isolation.yaml ~/pilot/templates/
cp ~/JetPack-1/src/pilot/templates/node-placement.yaml ~/pilot/templates/
cp ~/JetPack-1/src/pilot/templates/roles_data.yaml ~/pilot/templates/
cp ~/JetPack-1/src/pilot/templates/static-ip-environment.yaml ~/pilot/templates/
cp ~/JetPack-1/src/pilot/templates/nic-configs/5_port/delledgegpucompute.yaml ~/pilot/templates/nic-configs/5_port/
cp ~/JetPack-1/src/pilot/templates/nic-configs/5_port/delledgecompute.yaml ~/pilot/templates/nic-configs/5_port/
cp ~/JetPack-1/src/pilot/templates/nic-configs/5_port/nic_environment.yaml ~/pilot/templates/nic-configs/5_port/
cp ~/JetPack-1/src/pilot/templates/nic-configs/5_port/nic_environment.yaml ~/pilot/templates/nic-configs/5_port/
echo "Copying python mods for DCN"
# Already done pre-deployment on sah
# cp ~/JetPack-1/src/pilot/assign_role.py ~/pilot/
# cp ~/JetPack-1/src/pilot/constants.py ~/pilot/
# cp ~/JetPack-1/src/pilot/introspect_nodes.py ~/pilot/
# cp ~/JetPack-1/src/pilot/utils.py ~/pilot/
cp ~/JetPack-1/src/pilot/prep_overcloud_nodes.py ~/pilot/
cp ~/JetPack-1/src/pilot/discover_nodes/discover_nodes.py ~/pilot/discover_nodes/
cp ~/JetPack-1/src/pilot/undercloud.conf ~/pilot/

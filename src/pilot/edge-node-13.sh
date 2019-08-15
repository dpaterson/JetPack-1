#!/bin/bash

cd ~/pilot/discover_nodes; ./discover_nodes.py  -u root -p 'Dell0SS!' 192.168.111.13 > ~/edge-nodes-13.json
cd ~/pilot; ./config_idrac.py 192.168.111.13 -l DEBUG -n ~/edge-nodes-13.json
cd ~/pilot; ./import_nodes.py -l DEBUG -n ~/edge-nodes-13.json
cd ~/pilot; ./prep_overcloud_nodes.py -l DEBUG -a 192.168.111.13
cd ~/pilot; ./introspect_nodes.py -l DEBUG -a 192.168.111.13 -p edge-subnet
# cd ~/pilot; ./assign_role.py -l DEBUG -n ~/edge-nodes-13.json 192.168.111.13 compute-4

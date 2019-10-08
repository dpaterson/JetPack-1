cd ~/pilot/discover_nodes; ./discover_nodes.py  -u root -p 'Dell0SS!' 192.168.111.16 > ~/edge-nodes-16.json
cd ~/pilot; ./config_idrac.py 192.168.111.16 -n ~/edge-nodes-16.json
cd ~/pilot; ./import_nodes.py -n ~/edge-nodes-16.json
cd ~/pilot; ./prep_overcloud_nodes.py -a 192.168.111.16
cd ~/pilot; ./introspect_nodes.py -a 192.168.111.16 -p edge-subnet
# cd ~/pilot; ./assign_role.py -n ~/edge-nodes-16.json 192.168.111.16 compute-3

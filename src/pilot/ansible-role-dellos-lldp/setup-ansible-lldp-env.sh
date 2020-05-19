#!/bin/bash
# once this script has executed and hosts.ini is updated
# to match your switch environment run:
# ansible-playbook -vvvv -i inventory.ini lldp-pb.yaml
sudo yum install -y ansible
sudo ansible-galaxy install Dell-Networking.dellos-lldp
sudo cp /etc/ansible/ansible.cfg /etc/ansible/ansible.cfg.bup
sudo cp ./ansible.cfg /etc/ansible/

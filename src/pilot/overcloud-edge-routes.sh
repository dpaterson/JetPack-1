#!/bin/bash


# update ssh config
~/pilot/update_ssh_config.py

# controllers
for node in cntl0 cntl1 cntl2 ; do
  ssh ${node} "echo '192.168.111.0/24 via 192.168.120.1 dev em3' | sudo tee -a /etc/sysconfig/network-scripts/route-em3" ;
  ssh ${node} "echo '192.168.121.0/24 via 192.168.120.1 dev em3' | sudo tee -a /etc/sysconfig/network-scripts/route-em3" ;
  ssh ${node} "sudo ifdown em3 ; sudo ifup em3;" ;
done

# compute and storage
for node in nova0 nova1 nova2 stor0 stor1 stor2 ; do
  ssh ${node} "echo '192.168.121.0/24 via 192.168.120.1 dev em3' | sudo tee -a /etc/sysconfig/network-scripts/route-em3" ;
  ssh ${node} "sudo ifdown em3 ; sudo ifup em3;" ;
done


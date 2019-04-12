#!/bin/bash

VLAN=$1
shift
netem_cmd="sudo DEV0=$VLAN DEV1=null /root/netem.sh $@"
echo $netem_cmd
for i in 0 1 2; do 
    cntl="cntl${i}"
    echo $cntl
    scp netem.sh heat-admin@$cntl:~/
    ssh  heat-admin@$cntl "sudo chmod +x netem.sh;sudo mv netem.sh /root/"
    ssh  heat-admin@$cntl "$netem_cmd" 
done

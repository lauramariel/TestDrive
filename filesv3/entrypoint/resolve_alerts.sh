#!/bin/bash
# Resolve alerts on cluster
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"
#CONFIG="./config2.json" # delete after testing
echo $CONFIG

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end 
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

echo $PE_IP

# Add PE Key to known_hosts
ssh-keyscan $PE_IP | grep nistp521 > /root/.ssh/known_hosts

ssh nutanix@$PE_IP "source /etc/profile; for i in \`ncli alerts ls | grep ID | awk '{print \$3}'\`; do ncli alerts resolve ids=\$i; done"
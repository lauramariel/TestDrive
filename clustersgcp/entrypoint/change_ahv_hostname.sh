#!/bin/bash
set -ex

# Desired hostname
HOSTNAME="10-0-128-151-aws-us-west-2c"

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.cloud-us-west.ips[0][0]' /home/config.json)
PE_IP="${PE_IP%\"}"
PE_IP="${PE_IP#\"}"
echo $PE_IP

# Add PE Key to known_hosts
ssh-keyscan $PE_IP | grep nistp521 > /root/.ssh/known_hosts

ssh nutanix@$PE_IP "source /etc/profile
ssh root@\`ncli host ls | grep 'Hypervisor Address' | awk '{print \$4}'\` 'wget https://storage.googleapis.com/testdrive-templates/clusters/update_hostname_el6el7_v2.sh; bash update_hostname_el6el7_v2.sh \$HOSTNAME'
genesis stop acropolis; cluster start"
#!/bin/bash
# Inject lab data into PC for Prism Pro

# Inject Prism Pro fake data into PC
# Requires SSH keys to be set up first


set -ex

CONFIG="/home/config.json"

# Get PC IP, and strip suffix and prefix "
PC_IP=$(jq '.tdaas_pc.ips[0][0]' $CONFIG)
PC_IP="${PC_IP%\"}" # deletes the " from the end 
PC_IP="${PC_IP#\"}" # deletes the " from the beginning
echo $PC_IP

ssh nutanix@$PC_IP 'source /etc/profile
PC_DATA='https://storage.googleapis.com/ntnx-td-image-repo/seedPC517latest.zip'
PC_HOST=`hostname -I`
curl -L ${PC_DATA} -o /home/nutanix/seedPC.zip
unzip /home/nutanix/seedPC.zip
pushd /home/nutanix/lab/
/home/nutanix/lab/initialize_lab.sh ${PC_HOST} > /home/nutanix/initialize_lab.log 2>&1 &
popd'
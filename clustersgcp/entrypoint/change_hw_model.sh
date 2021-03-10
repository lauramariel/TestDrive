#!/bin/bash
# This script logs into the CVM and runs a script to change the HW model
#
set -ex

# Desired HW Model
HW_MODEL="AWS.z1d.metal"

#Get PE IP, and strip suffix and prefix
PE_IP=$(jq '.["cloud-us-west"].ips[0][0]' /home/config.json)
PE_IP="${PE_IP%\"}"
PE_IP="${PE_IP#\"}"
echo $PE_IP

# Add PE Key to known_hosts
ssh-keyscan $PE_IP | grep nistp521 > /root/.ssh/known_hosts

echo "Logging into CVM to update model name"
# Download and run the script
ssh nutanix@$PE_IP "source /etc/profile
cd /home/nutanix/bin
wget https://storage.googleapis.com/testdrive-templates/clusters/zeus_edit_model_name.py
sed -i 's/GCP/$HW_MODEL/g' zeus_edit_model_name.py
python zeus_edit_model_name.py"

if [ $? != 0 ]  
then
    exit 1
fi
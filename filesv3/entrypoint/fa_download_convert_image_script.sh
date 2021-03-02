#!/bin/bash
# Download convert_image.py script to CVM - req'd by engineering
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"

echo $FA_URL
echo $FA_METADATA_URL
echo $FA_FILEPATH
echo $FA_METAFILEPATH

#CONFIG="./config2.json"
# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end 
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

echo $PE_IP

echo "Downloading updated convert_image.py script to CVM"
ssh nutanix@$PE_IP "source /etc/profile; cd /home/nutanix; cp /home/nutanix/bin/convert_image.py /home/nutanix/bin/convert_image.py.orig; cd /usr/local/nutanix/bin/; curl -kSOL https://storage.googleapis.com/testdrive-templates/files/deepdive/convert_image.py"

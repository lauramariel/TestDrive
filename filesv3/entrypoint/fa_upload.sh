#!/bin/bash
# Download and upload File Analytics software
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"
FA="nutanix-file_analytics-el7.7-release-3.0.0-b82e5ac858f94df4b7b35fb4466f3e2392e4253f.qcow2"
FA_META="nutanix-file_analytics-el7.7-release-3.0.0-b82e5ac858f94df4b7b35fb4466f3e2392e4253f-metadata.json"

FA_URL="https://storage.googleapis.com/ntnx-td-image-repo/$FA"
FA_METADATA_URL="https://storage.googleapis.com/ntnx-td-image-repo/$FA_META"
FA_FILEPATH="/home/nutanix/$FA"
FA_METAFILEPATH="/home/nutanix/$FA_META"

echo $FA_URL
echo $FA_METADATA_URL
echo $FA_FILEPATH
echo $FA_METAFILEPATH

#CONFIG="./config2.json" # delete after testing
echo $CONFIG

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end 
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

#PE_IP="34.74.251.25"
echo $PE_IP

echo "Downloading File Analytics to CVM and uploading to Prism"
ssh nutanix@$PE_IP "source /etc/profile; cd /home/nutanix; curl -kSOL $FA_URL; curl -kSOL $FA_METADATA_URL; ncli software upload software-type=FILE_ANALYTICS file-path=$FA_FILEPATH meta-file-path=$FA_METAFILEPATH"
ssh nutanix@$PE_IP "source /etc/profile; cd /home/nutanix; ncli software upload software-type=FILE_ANALYTICS file-path=$FA_FILEPATH meta-file-path=$FA_METAFILEPATH"

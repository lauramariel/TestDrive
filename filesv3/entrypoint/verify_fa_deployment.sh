#!/bin/bash
# Verify FA deployment
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"

echo $FA_URL
echo $FA_METADATA_URL
echo $FA_FILEPATH
echo $FA_METAFILEPATH

CONFIG="./config2.json"
# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end 
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

echo $PE_IP

echo "Verifying FA deployment by checking for existence of zookeeper node /appliance/physical/afsfileanalytics"
ssh nutanix@$PE_IP "source /etc/profile; zkcat /appliance/physical/afsfileanalytics; "

# If status returned 0 
if [ "$?" -eq 1 ]
then
    echo "Check for zookeeper node returned an error"
    exit 1
else
    exit 0
fi
#!/bin/bash
#   
# Updates ZK with the proxy URL of FA to support
# direct access to File Analytics on Test Drive
#   
# Requires SSH keys to be set up first and FA to be deployed

set -ex

CONFIG="/home/config.json"
#CONFIG="./config4.json" # delete after testing
echo $CONFIG

UPDATE_FA_FILE_PATH="https://storage.googleapis.com/testdrive-templates/files/deepdive/fa_update_zk.tar"

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

echo $PE_IP

# Get AVM URL or IP
AVM_URL=$(jq .\"files-config\".'custom_config.files_url' $CONFIG) || AVM_URL=$(jq '.proxy_vm.public_uvms'.\"public-uvm-1\"'.external_ip' $CONFIG)

AVM_URL="${AVM_URL%\"}" # deletes the " from the end
AVM_URL="${AVM_URL#\"}" # deletes the " from the beginning

echo $AVM_URL

# update ZK with proxy URL
echo "Updating ZK with proxy URL"
ssh nutanix@$PE_IP "source /etc/profile
cd /home/nutanix
curl -kSOL $UPDATE_FA_FILE_PATH
tar -xvf fa_update_zk.tar -C /tmp
mv /tmp/fa_update_zk/* /home/nutanix/bin/
cd /home/nutanix/bin
python fa_update_zk_node.py --avm_ip=$AVM_URL"


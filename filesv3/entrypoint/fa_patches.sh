#!/bin/bash
# - Updates ZK with the proxy URL of FA to support
#   direct access to File Analytics on Test Drive
# - Need ability to support 443 (previously a patch upgrading to 1.1.1 was provided but we're now on 1.4.0)
# - rsync PE prism files to PC to support 443 for accessing PE through PC
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"
#CONFIG="./config3.json" # delete after testing
echo $CONFIG

UPDATE_FA_FILE_PATH="https://storage.googleapis.com/testdrive-templates/files/deepdive/fa_update_zk.tar"
UPDATE_MINERVA_PATH="https://storage.googleapis.com/testdrive-templates/files/deepdive/nutanix-minervacvm-el7.3-release-fsm-1.1.1-stable-e4a1334b74e7b8efa6d5d342bf7cce8e478164b2-x86_64.tar.gz"
MINERVA_PACKAGE_PATH="/home/nutanix/nutanix-minervacvm-el7.3-release-fsm-1.1.1-stable-e4a1334b74e7b8efa6d5d342bf7cce8e478164b2-x86_64.tar.gz"

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

ssh nutanix@$PE_IP "source /etc/profile
cd /home/nutanix
curl -kSOL $UPDATE_FA_FILE_PATH
tar -xvf fa_update_zk.tar -C /tmp
mv /tmp/fa_update_zk/* /home/nutanix/bin/
cd /home/nutanix/bin
python fa_update_zk_node.py --avm_ip=$AVM_URL"

# Todo
# port 443 support
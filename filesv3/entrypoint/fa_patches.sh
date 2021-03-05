#!/bin/bash
# - Updates ZK with the proxy URL of FA to support
#   direct access to File Analytics on Test Drive
# - Need ability to support 443 (previously a patch upgrading to 1.1.1 was provided but we're now on 1.4.0)
# - rsync PE prism files to PC to support 443 for accessing PE through PC
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"
#CONFIG="./config4.json" # delete after testing
echo $CONFIG

UPDATE_FA_FILE_PATH="https://storage.googleapis.com/testdrive-templates/files/deepdive/fa_update_zk.tar"
UPDATE_MINERVA_PATH="https://storage.googleapis.com/testdrive-templates/filesv3/deepdive/nutanix-minervacvm-el7.3-release-fsm-2.0.1-stable-4e7c964481d81415110700410eddaea920993df0-x86_64.tar.gz"
MINERVA_PKG_PATH="/home/nutanix/nutanix-minervacvm-el7.3-release-fsm-2.0.1-stable-4e7c964481d81415110700410eddaea920993df0-x86_64.tar.gz"

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

echo $PE_IP

# Get PC internal IP for copying to from CVM
PC_INT_IP=$(jq '.tdaas_pc.ips[0][1]' $CONFIG)
PC_INT_IP="${PC_INT_IP%\"}" # deletes the " from the end
PC_INT_IP="${PC_INT_IP#\"}" # deletes the " from the beginning

echo $PC_INT_IP

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

# port 443 support - upgrade patch to FSM 2.0.1

echo "Patching FSM to 2.0.1 for 443 support"
ssh nutanix@$PE_IP "source /etc/profile
cd /home/nutanix
curl -kSOL $UPDATE_MINERVA_PATH
upgrade_fsm.py --pkg_path=$MINERVA_PKG_PATH"

echo "rsync the Prism updates to PC for 443 support"
# rsync updates to PC
ssh nutanix@$PE_IP "source /etc/profile
rsync -rvz --delete --rsh='/usr/bin/sshpass -p \"nutanix/4u\" ssh -o StrictHostKeyChecking=no -l nutanix' \
/home/nutanix/prism/webapps/console/ nutanix@$PC_INT_IP:/home/nutanix/prism/webapps/console/el7.3-release-euphrates-5.19-stable-09739c1ac339c1505c9181577bb6a0436a936b3a/console"



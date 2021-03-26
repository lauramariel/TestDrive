#!/bin/bash
#
# Upgrade to FSM 2.0.1 with 443 support
#
# Requires SSH keys to be set up first
# This can be done prior to FA deployment

set -ex

CONFIG="/home/config.json"
#CONFIG="./config4.json" # delete after testing
echo $CONFIG

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
/home/nutanix/prism/webapps/console/ nutanix@$PC_INT_IP:/home/nutanix/prism/webapps/console/el7.3-release-euphrates-5.19.1-stable-b60761f1a700950a521d1520fccea1bac5deb288/console"

echo "Put the minerva patch back and restart minerva_cvm - DRIVE-768"
ssh nutanix@$PE_IP "source /etc/profile
cd /home/nutanix/minerva/bin
curl -kSOL https://storage.googleapis.com/testdrive-templates/filesv3/deepdive/minerva_cvm_test_patch.py
chmod 740 /home/nutanix/minerva/bin/minerva_cvm_test_patch.py
genesis stop minerva_cvm
cluster start"

echo "Done!"
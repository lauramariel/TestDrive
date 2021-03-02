#!/bin/bash
# Download and run script for populating fake data
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"
#CONFIG="./config2.json" # delete after testing
echo $CONFIG

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cluster.ips[0][0]' $CONFIG)
PE_IP="${PE_IP%\"}" # deletes the " from the end 
PE_IP="${PE_IP#\"}" # deletes the " from the beginning

echo $PE_IP

ssh nutanix@$PE_IP "source /etc/profile; for fs in \`afs info.fileservers | grep -v -i 'Fileserver' | awk '{print \$3}'\`; do echo \$fs; 
ssh nutanix@\$fs 'cd /home/nutanix/minerva/bin; wget https://storage.googleapis.com/testdrive-templates/files/populate_fs_metrics.py; python populate_fs_metrics.py 24 12; (crontab -l 2>/dev/null; echo \"*/30 * * * * /usr/bin/python /home/nutanix/minerva/bin/populate_fs_metrics.py 24 12\") | crontab -';
done"
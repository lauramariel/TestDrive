#!/bin/bash
# SSH into AutoDC from PC and configure the DNS zones
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"

# Get PC IP, and strip suffix and prefix "
PC_IP=$(jq '.tdaas_pc.ips[0][0]' $CONFIG)
PC_IP="${PC_IP%\"}" # deletes the " from the end 
PC_IP="${PC_IP#\"}" # deletes the " from the beginning
echo $PC_IP

# Install sshpass
# TODO: put RPM in google bucket
ssh nutanix@$PC_IP 'wget http://mirror.centos.org/centos/7/extras/x86_64/Packages/sshpass-1.06-2.el7.x86_64.rpm'
ssh nutanix@$PC_IP 'sudo rpm -i sshpass-1.06-2.el7.x86_64.rpm'

# login to AutoDC and configure the DNS zone
ssh nutanix@$PC_IP 'source /etc/profile; sshpass -pnutanix/4u ssh -o StrictHostKeyChecking=no root@172.31.0.41 samba-tool dns zonecreate dc 0.31.172.in-addr.arpa --username=administrator@ntnxlab.local --password="nutanix/4u"'
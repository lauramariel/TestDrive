#!/bin/bash
# Set aplos timeout on PE and PC
# Requires SSH keys to be set up first

set -ex

CONFIG="/home/config.json"

# Get PC IP, and strip suffix and prefix "
PC_IP=$(jq '.tdaas_pc.ips[0][0]' $CONFIG)
PC_IP="${PC_IP%\"}" # deletes the " from the end
PC_IP="${PC_IP#\"}" # deletes the " from the beginning
echo $PC_IP

ssh nutanix@$PC_IP 'sed -i 's/PERMANENT_SESSION_LIFETIME=900/PERMANENT_SESSION_LIFETIME=90000/g' /home/nutanix/aplos/config/aplos.cfg; genesis stop aplos aplos_engine && cluster start'

# Get PE IP, and strip suffix and prefix "
PE_IP=$(jq '.tdaas_cljuster.ips[0][0]' $CONFIG)
PE_IP="${PC_IP%\"}" # deletes the " from the end
PE_IP="${PC_IP#\"}" # deletes the " from the beginning
echo $PC_IP

ssh nutanix@$PE_IP 'sed -i 's/PERMANENT_SESSION_LIFETIME=900/PERMANENT_SESSION_LIFETIME=90000/g' /home/nutanix/aplos/config/aplos.cfg; genesis stop aplos aplos_engine && cluster start'
#!/bin/bash
function execute_command {
    echo "Executing: $@"
    eval $@
    rc=$?
    echo "Done"
    echo
    return $rc
}

cd "$(dirname "$0")"
echo ${CUSTOM_SCRIPT_CONFIG}

yum -y install $(cat yum_pkgs.txt)
pip3 install -r requirements.txt
execute_command "export NUTEST_PATH=/home"

python3 pc_eula_accept.py       # EULA Acceptance & Pulse Enablement - this might already be configured by another NX-on-GCP plugin
python3 pc_ntp.py               # Configure NTP
python3 pc_upload_images.py     # Upload required images defined in specs/upload_image_list.json
echo "Sleeping 10min to let images finish uploading"
sleep 600
python3 pc_create_vms.py        # Create VMs defined in specs/create_vm_list.json
sh create_ssh_keys.sh           # Create SSH keys for PC login
python3 pc_add_ssh_keys.py      # Add SSH keys to PC
sh configure_autodc.sh          # Configure Domain Controller with zones
python3 pc_authconfig.py        # Setup DC as an auth source for Prism Central
sh pc_fake_data.sh              # Inject PC fake data
echo "Sleeping 10min to let lab script finish"
sleep 600
#python3 pc_enable_calm.py

# TODO:
# Calm enablement (or use $ENABLE_CALM?) and all the Calm stuff
# Aplos timeout (if necessary)
# SMTP config
# Creation of DSIP/VIP (if not done already)
# Creation of network if required (if not done by $MANAGED_NETWORK)
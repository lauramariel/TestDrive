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
python3 pe_add_ssh_keys.py
python3 enable_files_manager.py
python3 lcm_inventory.py
python3 lcm_update_files_manager.py
python3 set_ad_ip.py
python3 configure_filer.py
python3 create_shares.py
# python3 disable_alerts.py
# python resolve_alerts.py
sh fa_upload.sh
# python3 fa_upload.py - no longer needed, do with bash script
# python fa_prep.py - left off here 2/28
# python fa_deploy.py
# sleep 60
# python fa_register.py
# python fa_patches.py

# sleep to ensure that Windows VM startup script is 
# finished before deployment is marked as complete
sleep 600
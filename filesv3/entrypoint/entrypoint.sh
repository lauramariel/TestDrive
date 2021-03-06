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
yum -y install epel-release
yum -y install $(cat yum_pkgs.txt)
pip3 install -r requirements.txt
execute_command "export NUTEST_PATH=/home"
sh create_ssh_keys.sh
python3 pe_add_ssh_keys.py
python3 enable_files_manager.py
python3 lcm_inventory.py
python3 lcm_update_files_manager.py
python3 set_ad_ip.py
python3 configure_filer.py
python3 create_shares.py
sh fs_populate_data.sh
#python3 disable_alerts.py
#sh resolve_alerts.sh
sh upgrade_fsm.sh
sh fa_upload.sh
sh fa_download_convert_image_script.sh
python3 fa_prep.py
python3 fa_deploy.py
sh verify_fa_deployment.sh
python3 fa_register.py
sh update_zk_for_fa.sh
python3 pe_disable_alerts.py tdaas_cluster
python3 pc_disable_alerts.py
python3 pe_resolve_alerts.py tdaas_cluster
python3 pc_resolve_alerts.py
python3 delete_extra_cent_vm.py
# sleep to ensure that Windows VM startup script is 
# finished before deployment is marked as complete
sleep 600

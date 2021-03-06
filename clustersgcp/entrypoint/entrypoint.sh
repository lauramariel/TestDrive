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

echo "Creating SSH keys"
sh create_ssh_keys.sh
echo "Adding SSH keys to PE for password-less login"
python3 pe_ssh_keys.py cloud-us-west
sleep 60
echo "Changing HW Model"
sh change_hw_model.sh
echo "Changing AHV hostname"
sh change_ahv_hostname.sh
echo "Sleeping 60 seconds"
sleep 60

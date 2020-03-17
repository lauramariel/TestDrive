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
#python sample.py
python deploy_autodc.py
python set_ntp_dns.py
python configure_filer.py
python create_smb_share.py
#python upload_file_analytics.py
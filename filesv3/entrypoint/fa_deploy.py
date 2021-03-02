"""
fa_deploy.py: automation to deploy File Analytics
on an NX-on-GCP cluster

Author: laura@nutanix.com
Date:   2020-07-16
"""

import sys
import os
import json
import time
import requests

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def update_fa_spec(ip, auth):
    # Get the Container UUID from file server listing
    url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers"
    headers = {'Content-type': 'application/json'}
    resp = requests.get(url, auth=auth, headers=headers, verify=False)
    if resp.ok:
        details = resp.json()
        for fs in details.get("entities"):
            if "primary" in fs.get("name"):
                fs_name = fs.get("name")
                ctr_id = fs.get("containerUuid")
    else:
        print(f">>> Error getting FS details {resp.text}")
        sys.exit(1)
    print(f"Container UUID for {fs_name} : {ctr_id}")

    # Get Container name from container listing
    url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/storage_containers"
    headers = {"Content-type": "application/json"}
    resp = requests.get(
        url, auth=auth, headers=headers, verify=False
    )
    if resp.ok:
        details = resp.json()
        for ctr in details.get("entities"):
            if ctr_id in ctr.get("storage_container_uuid"):
                ctr_name = ctr.get("name")
    else:
        print(f">>> Error getting ctr details {resp.text}")
        sys.exit(1)
    print(f"Container Name for {fs_name}: {ctr_name}")

    # Get Network UUID from the network spec which was already updated
    # in a previous script
    f = open("specs/network_config.json", "r")
    network_spec = json.load(f)
    f.close()
    network_uuid = network_spec["uuid"]
    print(f"Network UUID: {network_uuid}")

    # Now let's update the FA deploy payload/spec
    # read existing spec in
    f = open("specs/analytics_config.json", "r")
    facfg = json.load(f)
    f.close()
    facfg["container_uuid"] = ctr_id
    facfg["container_name"] = ctr_name
    facfg["network"]["uuid"] = network_uuid

    # write the new spec
    f = open("specs/analytics_config.json", "w")
    json.dump(facfg, f)
    f.close()

    print("analytics_config.json updated successfully!")


def deploy_fa(ip, auth):
    # model for deploying FA
    f = open("specs/analytics_config.json", "r")
    facfg = json.load(f)
    f.close()

    url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/analyticsplatform"
    data = json.dumps(facfg)
    print(f">>> Url: {url} Payload: {data}")
    headers = {"Content-type": "application/json"}
    resp = requests.post(url, auth=auth, headers=headers, data=data, verify=False,)
    print(resp)

    if not resp.ok:
        print(f">>> Error deploying FA {resp.text}")
        sys.exit(1)

    # wait for deployment to finish
    print(f"Sleeping for 20 minutes")
    time.sleep(1200)

    # # make sure deployment completed
    # print(
    #     "Checking for contents of zkcat /appliance/physical/afsfileanalytics to ensure FA deployed"
    # )
    # resp = cluster.execute("zkcat /appliance/physical/afsfileanalytics")
    # print(resp)
    # if len(resp.get("stdout")) < 10:
    #     print("No FA info found in stdout!")
    #     #sys.exit(1)


def delete_vm(ip, auth, vm_name):
    # Get the VM UUID
    url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/vms"
    headers = {"Content-type": "application/json"}
    resp = requests.get(url, auth=auth, headers=headers, verify=False,)
    print(resp)

    if resp.ok:
        details = resp.json()
        for vm in details.get("entities"):
            if vm_name in vm.get("name"):
                vm_uuid = vm.get("uuid")
    else:
        print(f">>> Error getting VMs {resp.text}")
        sys.exit(1)

    # Delete the VM
    url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/vms/{vm_uuid}"
    headers = {"Content-type": "application/json"}
    resp = requests.delete(url, auth=auth, headers=headers, verify=False,)
    print(resp)

    if not resp.ok:
        print(f">>> Error deleting VM {resp.text}")

def main():
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)
    cvm_info = config.get("tdaas_cluster")
    pe_ip = cvm_info.get("ips")[0][0]
    pe_password = cvm_info.get("prism_password")

    # pc_ip = "34.74.139.172"
    # pc_password = 'STJeVIMN*9Y'

    # pe_ip = "34.74.251.25"
    # pe_password = 'VKMOCQy2*Y'

    pe_auth = HTTPBasicAuth("admin", f"{pe_password}")
    #pc_auth = HTTPBasicAuth("admin", f"{pc_password}")

    # Update FA spec
    update_fa_spec(pe_ip, pe_auth)

    # Deploy FA
    print("Deploying FA - will take up to 20 minutes")
    deploy_fa(pe_ip, pe_auth)

    # delete the sampleVM we created in fa_prep.py to work around IP address issue
    print("Deleting the placeholder VM")
    delete_vm(pe_ip, pe_auth, "SampleVM")
    print("Finished!")
    sys.exit(0)


if __name__ == "__main__":
    main()

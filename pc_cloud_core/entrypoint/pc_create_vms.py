"""
pc_create_vms.py: automation to deploy VMs
onto Prism Central based on a spec called
create_vm_list.json

Author: laura@nutanix.com
Date:   2020-12-30
"""

import requests
import json
import os
import sys
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def get_image_uuid(image, pc_external_ip, pc_password):
    print(f"Getting Image UUID for {image}")
    url = f"https://{pc_external_ip}:9440/api/nutanix/v3/images/list"
    payload = { "kind": "image" }
    headers = { "Content-type": "application/json" }
    resp = requests.post(url, auth=HTTPBasicAuth("admin", pc_password), headers=headers, data=json.dumps(payload), verify=False)
    print(f"Response: {resp}")
    if resp.ok:
        image_info = json.loads(resp.text)
    else:
        sys.exit(1)

    # need to match name with .entities[].status.name
    # and then look up .entities[].metadata.uuid for the corresponding array element
    image_uuid = False

    for i in image_info["entities"]:
        if i["status"]["name"] == image:
            image_uuid = i["metadata"]["uuid"]

    return image_uuid

def get_network_info(pe_external_ip, pe_password):
    print(f"Getting Network Info")
    url = f"https://{pe_external_ip}:9440/PrismGateway/services/rest/v2.0/networks"
    headers = { "Content-type": "application/json" }
    resp = requests.get(url, auth=HTTPBasicAuth("admin", pe_password), headers=headers, verify=False)
    print(f"Response: {resp}")
    if resp.ok:
        network_info = json.loads(resp.text)
    else:
        sys.exit(1)

    return network_info

def create_vm(vm_data, network_spec, network_info, pc_external_ip, pc_password):
    
    url = f"https://{pc_external_ip}:9440/api/nutanix/v3/vms"

    print(f"Creating VM {vm_data['name']}")

    with open('specs/create_vm_payload.json') as f:
        vm_payload = json.load(f)
        f.close()

    # get image UUID for the VM we are creating
    vm_image = vm_data["image"]
    image_uuid = get_image_uuid(vm_image, pc_external_ip, pc_password)

    if not image_uuid:
        print(f"ERROR: UUID for {vm_image} not found")
        sys.exit(1)

    print(f"Image UUID for {vm_data['name']} is {image_uuid}")

    # get network UUID
    network_uuid = False
    for i in network_info["entities"]:
        if i["name"] == network_spec["name"]:
            network_uuid = i["uuid"]

    if not network_uuid:
        print(f"ERROR: network UUID for {network_spec['name']} not found")
        sys.exit(1)
    
    print(f"Network UUID for {network_spec['name']} is {network_uuid}")

    # Modify payload with image and network info
    vm_payload["spec"]["resources"]["disk_list"][0]["data_source_reference"]["uuid"] = image_uuid
    vm_payload["spec"]["resources"]["nic_list"][0]["subnet_reference"]["name"] = network_spec["name"]
    vm_payload["spec"]["resources"]["nic_list"][0]["subnet_reference"]["uuid"] = network_uuid

    count = 0

    # if more than one, give each a distinct name
    while count < vm_data["number"]:
        if vm_data["number"] == 1:
            # just one VM, no need for prefix
            vm_payload["spec"]["name"] = vm_data["name"]    
        elif vm_data["number"] > 1:
            vm_payload["spec"]["name"] = f"{vm_data['name']}-{count}"
        else:
            print(f"ERROR: invalid number of VMs specified for {vm_data['name']}")
            sys.exit(1)

        # specify the IP if it's given
        if vm_data["ip"]:
            vm_payload["spec"]["resources"]["nic_list"][0]["ip_endpoint_list"][0]["ip"] = vm_data["ip"]

        print("VM Payload: " + json.dumps(vm_payload))
        headers = {'Content-type': 'application/json'}
        resp = requests.post(url, auth=HTTPBasicAuth("admin", pc_password), headers=headers, data=json.dumps(vm_payload), verify=False)
        print(f"Response: {resp}")
        print(f"Response Details: {resp.text}")

        count += 1

def main():
    # Get and log the config from the Env variable
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)

    # Get PC info from the config dict
    pc_info = config.get("tdaas_pc")
    pc_external_ip = pc_info.get("ips")[0][0]
    #pc_internal_ip = pc_info.get("ips")[0][1]
    pc_password = pc_info.get("prism_password")

    # Get CVM info from the config dict
    pe_info = config.get("tdaas_cluster")
    pe_external_ip = pe_info.get("ips")[0][0]
    #pe_internal_ip = pc_info.get("ips")[0][1]
    pe_password = pe_info.get("prism_password")

    # Get the network spec
    with open('specs/network_spec.json') as f:
        network_spec = json.load(f)
        f.close()
    
    # Get existing network info from cluster
    network_info = get_network_info(pe_external_ip, pe_password)
    if not network_info:
        print(f"ERROR: Network info not found")
        sys.exit(1)

    # VM Spec
    with open('specs/create_vm_list.json') as f:
        vm_list = json.load(f)
        f.close()

    for vm_data in vm_list["vms"]:
        print(f"{vm_data}")
        create_vm(vm_data, network_spec, network_info, pc_external_ip, pc_password)
    
if __name__ == '__main__':
    main()
# Script to upload images for TD2:
# UbuntuDesktop1604
# AutoDC2

import requests
import json
import config
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ip=config.IP
password=config.PASSWORD

# have to get image and network UUID first

def create_vm(vm_data):
        url = f"https://{ip}:9440/api/nutanix/v3/images"

        with open('create_vm.json') as f:
            payload = json.load(f)
            f.close()

        print("Payload: " + json.dumps(payload))
        headers = {'Content-type': 'application/json'}
        resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=json.dumps(payload), verify=False)
        print(f"Response: {resp}")
        print(f"Response Details: {resp.text}")

def main():
    vms=[{"name": "UbuntuDesktop1604", "vcpu": 2, "cores_per_cpu": 1, "memory": 2048, "number": 3},
         {"name": "AutoDC2", "vcpu": 2, "cores_per_cpu": 1, "memory": 2048, "number": 1}]

    for vm in vms:
        print(f"{vm}")
        create_vm(vm_data=vm)
    
if __name__ == '__main__':
    main()
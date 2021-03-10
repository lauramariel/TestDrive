"""
delete_extra_cent_vm.py: Delete the second cent_vm1 
  that is created as part of the second $AFS call

Author:   laura@nutanix.com
Date:     2021-03-10
"""

import sys
import os
import json
import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def delete_vm(auth, ip, vm_name):
  print(f">>> Checking for powered off {vm_name}")
  # Get the VM UUID
  url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/vms"
  headers = {"Content-type": "application/json"}
  resp = requests.get(url, auth=auth, headers=headers, verify=False,)
  print(resp)

  if resp.ok:
      details = resp.json()
      for vm in details.get("entities"):
          if vm_name in vm.get("name"):
            if "off" in vm.get("power_state"):
              vm_uuid = vm.get("uuid")
  else:
      print(f">>> Error getting VMs {resp.text}")
      sys.exit(1)

  # Delete the VM
  url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/vms/{vm_uuid}"
  headers = {"Content-type": "application/json"}
  resp = requests.delete(url, auth=auth, headers=headers, verify=False,)
  print(resp)

  if resp.ok:
    print(f">>> Deleted!")
  else:
      print(f">>> Error deleting VM {resp.text}")

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  pe_info = config.get("tdaas_cluster")
  pe_ip = pe_info.get("ips")[0][0]
  pe_password = pe_info.get("prism_password")

  auth = HTTPBasicAuth("admin", f"{pe_password}")
  vm_name = "cent_vm1"

  print(f">>> Deleting extra {vm_name}")
  delete_vm(auth, pe_ip, vm_name)

if __name__ == '__main__':
  main()

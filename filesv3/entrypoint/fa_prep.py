"""
fa_prep.py: custom config for FA on NX-on-GCP

This script does the following to support File Analytics on GCP:

1. Narrows the public-net pool range to 2 internal UVM IPs 
   associated with the external IPs provided by NX-on-GCP via proxy and
   sets AutoDC IP as the DNS server for public-net.
2. Creates a VM using the second IP so when deployed, File Analytics
   will get the first IP and we can control which one it gets.

This is to workaround the requirement that File Analytics has
to be deployed in a managed network and we are unable to define the IP
when deploying.

Updates:
2021-02-28 - Move to python3, no longer using nutest libraries

Author:   laura@nutanix.com
Date:     2020-07-16
Updated:  2021-02-28
"""

import os
import sys
import json
import time
import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def update_network_spec(ip, auth, network_name, start, end):
  # Get network info (UUID, VLAN) and update the network spec 
  # with the specified IP range
  url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/networks"  
  print(f">>> Url: {url}")
  headers = {'Content-type': 'application/json'}
  resp = requests.get(url, auth=auth, headers=headers, verify=False)
  print(resp)
  print(resp.text)

  if resp.ok:
    details = resp.json()
    for network in details.get("entities"):
      if network.get("name") == network_name:
        network_uuid = network.get("uuid")
        vlan_id = network.get("vlan_id")
  else:
    print(f">>> Error getting network info for {network_name}: {resp.text}")
    sys.exit(1)

  print(f">>> Network UUID found: {network_uuid}")
  print(f">>> Network VLAN found: {vlan_id}")

  # Update network spec
  f = open("specs/network_config.json", "r")
  network_spec = json.load(f)
  f.close()
  network_spec["vlanId"] = f"{vlan_id}"
  network_spec["uuid"] = f"{network_uuid}"
  network_spec["ipConfig"]["pool"][0]["range"] = f"{start} {end}"
  f = open("specs/network_config.json", "w")
  json.dump(network_spec, f)
  f.close()

  # update VM spec file while we're here for the dummy VM
  f = open("specs/sample_vm_spec.json", "r")
  vm_spec = json.load(f)
  f.close()
  vm_spec["vm_nics"][0]["network_uuid"] = network_uuid
  f = open("specs/sample_vm_spec.json", "w")
  json.dump(vm_spec, f)
  f.close()

  print(f"Updated network spec: {network_spec}")
  return network_spec
  
def update_network(spec, ip, auth):
  uuid = spec["uuid"]
  url = f"https://{ip}:9440/api/nutanix/v0.8/networks/{uuid}"  
  print(f">>> Url: {url}")
  headers = {'Content-type': 'application/json'}
  resp = requests.put(url, auth=auth, headers=headers, data=json.dumps(spec), verify=False)
  print(resp)

  if not resp.ok:
    print(f">>> Error updating network {uuid}: {resp.text}")

def create_sample_vm(ip, auth, vm_ip):
  f = open("specs/sample_vm_spec.json")
  vm_spec = json.load(f)
  f.close()
  vm_spec["vm_nics"][0]["requested_ip_address"] = vm_ip
  f = open("specs/sample_vm_spec.json", "w")
  json.dump(vm_spec, f)
  f.close()

  url = f"https://{ip}:9440/PrismGateway/services/rest/v2.0/vms"
  print(f">>> Url: {url}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(vm_spec), verify=False)
  print(resp)

  if not resp.ok:
    print(f">>> Error creating placeholder VM: {resp.text}")

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  print(config)
  cvm_info = config.get("tdaas_cluster")
  pe_ip = cvm_info.get("ips")[0][0]
  pe_password = cvm_info.get("prism_password")
  proxy_vm = config.get("proxy_vm")
  # get the internal IPs that were assigned and determine what the range should be
  public_uvm_1 = proxy_vm["public_uvms"]["public-uvm-1"]["internal_ip"]
  public_uvm_2 = proxy_vm["public_uvms"]["public-uvm-2"]["internal_ip"]

  #pc_ip = "34.74.139.172"
  #pc_password = 'STJeVIMN*9Y'

  #pe_ip = "34.74.251.25"
  #pe_password = 'VKMOCQy2*Y'

  pe_auth = HTTPBasicAuth("admin", f"{pe_password}")
  #pc_auth = HTTPBasicAuth("admin", f"{pc_password}")
  # get the internal IPs that were assigned and determine what the range should be
  public_uvm_1 = "10.31.0.2"
  public_uvm_2 = "10.31.0.3"

  # get the last octet of the IPs and see which one is the smaller one
  uvm_1_last_octet = [ int(a) for a in public_uvm_1.split('.')][3]
  uvm_2_last_octet = [ int(a) for a in public_uvm_2.split('.')][3]

  if min(uvm_1_last_octet, uvm_2_last_octet) == uvm_1_last_octet:
      start = public_uvm_1
      end = public_uvm_2
  else:
      start = public_uvm_2
      end = public_uvm_1

  # update public-net to narrow the range to 2 IPs
  print(f">>> Start IP will be set to: {start}")
  print(f">>> End IP will be set to: {end}")

  spec = update_network_spec(ip=pe_ip, auth=pe_auth, network_name="public-net", start=start, end=end)
  update_network(spec, pe_ip, pe_auth)

  # create placeholder VM to use the second IP (end of the range)
  # using PE v2 APIs
  print(">>> Creating a placeholder VM to use up one of the IPs")
  create_sample_vm(pe_ip, pe_auth, end)

  sys.exit(0)

if __name__ == '__main__':
  main()

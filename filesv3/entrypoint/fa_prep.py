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

import sys
import os
import json
import time
import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_network_uuid(ip, auth, network_name):
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
  else:
    print(f">>> Error getting UUID for {network_name}: {resp.text}")

  print(f"Network UUID found: {network_uuid}")

  return network_uuid  
  
def update_network(uuid, ip, auth, start, end):
  url = f"https://{ip}:9440/api/nutanix/v0.8/networks/{uuid}"  
  print(f">>> Url: {url}")
  headers = {'Content-type': 'application/json'}
  #{"name":"public-net","vlanId":"2","ipConfig":{"dhcpOptions":{"domainNameServers":"172.31.0.41"},"dhcpServerAddress":"10.31.0.254","networkAddress":"10.31.0.0","prefixLength":"24","defaultGateway":"10.31.0.1","pool":[{"range":"10.31.0.2 10.31.0.3"}]},"uuid":"c427ae49-9491-44da-bd07-090ed746fd76","logicalTimestamp":7}
  data = {"name":"public-net","vlanId":"2","ipConfig":{"dhcpOptions":{"domainNameServers":"172.31.0.41"},"dhcpServerAddress":"10.31.0.254","networkAddress":"10.31.0.0","prefixLength":"24","defaultGateway":"10.31.0.1","pool":[{"range":"10.31.0.2 10.31.0.3"}]},"uuid":uuid}
  resp = requests.put(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)

  if not resp.ok:
    print(f">>> Error updating network {uuid}: {resp.text}")

  # print("Deleting the existing pool for network public-net")
  # resp = cluster.execute("acli net.delete_dhcp_pool public-net start=10.31.0.10", timeout=300)
  # print(resp)
  # print("Adding a new pool for network public-net")
  # resp = cluster.execute("acli net.add_dhcp_pool public-net start={} end={}".format(start, end), timeout=300)
  # print(resp)
  # print("Clearing DHCP/DNS config for network public-net")
  # resp = cluster.execute("acli net.clear_dhcp_dns public-net")
  # print(resp)
  # print("Adding AutoDC IP as the DNS server to public-net")
  # resp = cluster.execute("acli net.update_dhcp_dns public-net servers=172.31.0.41")
  # print(resp)

def create_vm(cluster, ip):
  print("Creating a dummy VM on {}".format(ip))
  resp = cluster.execute('acli vm.create SampleVM')
  print(resp)
  time.sleep(1)
  resp = cluster.execute('acli vm.nic_create SampleVM ip={ip} network={network}'.format(ip=ip, network="public-net"))
  print(resp)

def main():
  # config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  # print(config)
  # cvm_info = config.get("tdaas_cluster")
  # cvm_ip = cvm_info.get("ips")[0][0]
  # proxy_vm = config.get("proxy_vm")
  # # get the internal IPs that were assigned and determine what the range should be
  # public_uvm_1 = proxy_vm["public_uvms"]["public-uvm-1"]["internal_ip"]
  # public_uvm_2 = proxy_vm["public_uvms"]["public-uvm-2"]["internal_ip"]

  pc_ip = "34.74.139.172"
  prism_password = 'STJeVIMN*9Y'

  cvm_ip = "34.74.251.25"
  pe_password = 'VKMOCQy2*Y'

  pe_auth = HTTPBasicAuth("admin", f"{pe_password}")
  auth = HTTPBasicAuth("admin", f"{prism_password}")
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
  print(f"Start IP will be set to: {start}")
  print(f"End IP will be set to: {end}")

  network_uuid = get_network_uuid(ip=cvm_ip, auth=pe_auth, network_name="public-net")
  print(f"Network UUID: {network_uuid}")
  update_network(network_uuid, cvm_ip, pe_auth, start, end)

  # create dummy VM to use one of the IPs
  #print("Creating a dummy VM")
  #create_vm(ip=public_uvm_2)

  sys.exit(0)

if __name__ == '__main__':
  main()

"""
set_ad_ip.py

After running this script:
- Set AD IP in the config used by other scripts
- Sets based on AutoDC IP. If AutoDC IP doesn't exist
- then use Cloudflare DNS 1.1.1.1

Updates:
2021-02-26 - No longer using nutest libraries. Use APIs instead of logging
  into cluster.

Author:   laura@nutanix.com
Date:     2020-05-08
Updated:  2021-02-26
"""

import sys
import os
import json
import requests

from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def set_ad_ip(auth, ip, auto_dc_vm):
  print(f"Getting {auto_dc_vm} IP")

  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/api/nutanix/v3/vms/list"
  data = { "kind": "vm" }
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)  
  details = resp.json()

  # dns_ip will either be set to AutoDC IP
  # or to 1.1.1.1 if AutoDC VM is not found
  dns_ip = ""

  for i in range(len((details.get("entities")))):
    if details.get("entities")[i].get("status").get("name") == "AutoDC2":
      nic_info = details.get("entities")[i].get("status").get("resources").get("nic_list")
      dns_ip = nic_info[0].get("ip_endpoint_list")[0].get("ip")
      print(dns_ip)
  
  if not dns_ip:
    print(f">>> {auto_dc_vm} VM not found, defaulting to 1.1.1.1")
    dns_ip = "1.1.1.1"

  # get config files and set the appropriate keys
  print(f">>> Writing {dns_ip} to config files")

  # Clean this up later
  f = open("specs/ad_config.json", "r")
  adconfig = json.load(f)
  f.close()
  adconfig["ad_server_ip"] = f"{dns_ip}"
  f = open("specs/ad_config.json", "w")
  json.dump(adconfig, f)
  f.close()

  f = open("specs/ntp_dns_config.json", "r")
  dnsconfig = json.load(f)
  f.close()
  dnsconfig["dns_server"] = f"{dns_ip}"
  f = open("specs/ntp_dns_config.json", "w")
  json.dump(dnsconfig, f)
  f.close()

  f = open("specs/network_config.json", "r")
  netconfig = json.load(f)
  f.close()
  netconfig["ipConfig"]["dhcpOptions"]["domainNameServers"] = f"{dns_ip}"
  f = open("specs/network_config.json", "w")
  json.dump(netconfig, f)
  f.close()

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  print(config)

  pc_info = config.get("tdaas_pc")
  pc_ip = pc_info.get("ips")[0][0]
  pc_password = pc_info.get("prism_password")

  # pc_ip = "34.74.139.172"
  # pc_password = 'STJeVIMN*9Y'

  auto_dc_vm = "AutoDC2"

  auth = HTTPBasicAuth("admin", f"{pc_password}")

  # set AD IP based on AutoDC VM if it exists
  set_ad_ip(auth, pc_ip, auto_dc_vm)

  sys.exit(0)

if __name__ == '__main__':
  main()
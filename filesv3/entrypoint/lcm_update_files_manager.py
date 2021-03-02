"""
lcm_update_files_manager.py: Update Files Manager
using LCM API (available in LCM 2.4+)

Inventory must be done first

Author:   laura@nutanix.com
Date:     2021-02-24
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  pc_info = config.get("tdaas_pc")
  pc_ip = pc_info.get("ips")[0][0]
  prism_password = pc_info.get("prism_password")

  auth = HTTPBasicAuth("admin", f"{prism_password}")

  #
  # Get Files Manager UUID
  #
  print("Getting Files Manager UUID")
  headers = {'Content-Type': 'application/json'}
  url = f"https://{pc_ip}:9440/lcm/v1.r0.b1/resources/entities/list"
  data = { "filter": "entity_model==Files Manager"}
  print(f"Url: {url} Payload: {data}")
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp) 
  
  if resp.ok:
    details = resp.json()
    uuid = details.get("data").get("entities")[0].get("uuid")
    print(f"UUID: {uuid}")
  else:
    print(f"Error getting Files Manager UUID: {resp.text}")
    sys.exit(1)

  #
  # Create Plan for Upgrading Files Manager
  #
  print("Creating Plan for Upgrading Files Manager to 2.0.0")
  headers = {'Content-Type': 'application/json'}
  url = f"https://{pc_ip}:9440/lcm/v1.r0.b1/resources/plan"
  data = [{ "version": "2.0.0", "entity_uuid": uuid }]
  print(f"Url: {url} Payload: {data}")
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)

  if resp.ok:
    plan = resp.json()
    print(plan)
  else:
    print(f"Error creating plan: {resp.text}")
    sys.exit(1)

  #
  # Upgrade Files Manager
  #
  print("Upgrading Files Manager to 2.0.0")
  headers = {'Content-Type': 'application/json'}
  url = f"https://{pc_ip}:9440/lcm/v1.r0.b1/operations/update"
  data = { "entity_update_spec_list": [ { "version": "2.0.0", "entity_uuid": uuid}]}
  print(f"Url: {url} Payload: {data}")
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)

  if resp.ok:
    details = resp.json()
    print(details)
  else:
    print(f"Error updating Files Manager: {resp.text}")
    sys.exit(1)

if __name__ == '__main__':
  main()

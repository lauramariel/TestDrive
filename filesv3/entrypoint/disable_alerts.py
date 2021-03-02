"""
disable-alerts.py: automation to disable the File Server
capacity alerts on PE due to synthetic File Server data
being populated

After running this script:
- Following alerts should be disabled on PE:
  - A160000 File Server Space Usage High
  - A160001 File Server Space Usage Critical
  - A160010 File server multiple VMs on single node check

Author:   laura@nutanix.com
Date:     2020-05-06
"""

import sys
import os
import json
import time
import requests
import pdb
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_alert_id(auth, ip, id):
  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/health_checks?includeInternalChecks=true"
  resp = requests.get(url, auth=auth, headers=headers, verify=False)
  if resp.ok:
    details = json.loads(resp.content)
    for i in details:
      if id in i['id']:
        full_alert_id = i['id']
  else:
    # didn't work, just return some invalid number
    full_alert_id = -1

  return full_alert_id

def disable_alert(auth, ip, id, full_id):
  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/health_checks"
  data = {"alertTypeId": f"A{id}", "id": f"{full_id}", "enabled": False, "modifiedByUsername": "admin"}
  resp = requests.put(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  prism_password = cvm_info.get("prism_password")
  
  #cvm_external_ip = "35.185.229.192"
  #prism_password = "GWhQZ9*KC4L65"

  auth = HTTPBasicAuth("admin", f"{prism_password}")

  alert_ids = ["160000", "160001", "160010"]
 
  # For each alert_id, call function to get full alert id
  # which is of the form cluster-id:alert-id
  # and then disable it

  for i in alert_ids:
    print(f"Processing {i}")
    print("Getting full alert id")
    short_alert_id = i
    id = get_alert_id(auth, cvm_external_ip, short_alert_id)

    if id == -1:
      print("Invalid alert ID")
      exit(0) #exit 0 so we don't break the whole deployment

    print(f"ID: {id}")
    # Call function to disable alert based on returned ID
    print(f"Disabling alert {id}")
    disable_alert(auth, cvm_external_ip, short_alert_id, id)

if __name__ == '__main__':
  main()

"""
enable_files_manager.py: Enable Files Manager on PC

Author:   laura@nutanix.com
Date:     2021-02-24
"""

import os
import json
import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def enable_files_manager(auth, ip):
  print(f"Enabling Files Manager")
  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/api/nutanix/v3/services/files_manager"
  data = { "state": "ENABLE" }
  print(f">>> Url: {url} Payload: {data}")
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)
  print(resp.text)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  pc_info = config.get("tdaas_pc")
  pc_ip = pc_info.get("ips")[0][0]
  pc_password = pc_info.get("prism_password")

  auth = HTTPBasicAuth("admin", f"{pc_password}")

  enable_files_manager(auth, pc_ip)

if __name__ == '__main__':
  main()

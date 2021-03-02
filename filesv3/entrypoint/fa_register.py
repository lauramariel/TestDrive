"""
fa_register.py: automation to register file analytics
with a file server

Author: laura@nutanix.com
Date:   2020-07-30
"""

import sys
import os
import json
import time
import requests

from configure_filer import get_fs_uuid
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def register_fa(fa_ip, auth, fs_uuid):
  # model for deploying FA
  with open('specs/fa_register.json') as f:
    facfg = json.load(f)
    f.close()

  # AD info
  with open('specs/ad_config.json') as f:
    adconfig = json.load(f)
    f.close()

  domain = adconfig.get("ad_domain_name")
  ad_admin_user = adconfig.get("ad_admin_user")
  ad_admin_pass = adconfig.get("ad_admin_pass")
 
  # Set up payload
  facfg["dns_domain_name"] = domain
  facfg["file_server_uuid"] =  fs_uuid
  facfg["ad_credentials"]["username"] = ad_admin_user
  facfg["ad_credentials"]["domain"] = domain
  facfg["ad_credentials"]["password"] = ad_admin_pass
 
  url = f"https://{fa_ip}:3000/fa/api/v1/fileservers/subscription?file_server_uuid={fs_uuid}&user_name=admin"
  data = json.dumps(facfg)
  print(f">>> Url: {url} Payload: {data}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=auth, headers=headers, data=data, verify=False)
  print(resp)
  print(resp.text)

  if not resp.ok:
    print(f">>> Error registering FS to FA: {resp.text}")

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  print(config)
  cvm_info = config.get("tdaas_cluster")
  pe_ip = cvm_info.get("ips")[0][0]
  pe_password = cvm_info.get("prism_password")

  # public_uvm_1 is the FA server 
  proxy_vm = config.get("proxy_vm")
  public_uvm_1 = proxy_vm["public_uvms"]["public-uvm-1"]["external_ip"]

  # pe_ip = "34.74.251.25"
  # pe_password = 'VKMOCQy2*Y'

  pe_auth = HTTPBasicAuth("admin", f"{pe_password}")

  # public_uvm_1 = "35.229.90.36"

  # get the FS UUID of the primary file server
  url = f"https://{pe_ip}:9440/PrismGateway/services/rest/v1/vfilers"
  headers = {'Content-type': 'application/json'}
  resp = requests.get(url, auth=pe_auth, headers=headers, verify=False)
  if resp.ok:
      details = resp.json()
      for fs in details.get("entities"):
          if "primary" in fs.get("name"):
              fs_uuid = fs.get("uuid")

  # deploy FA
  print(f"Registering file server {fs_uuid} with FA")
  register_fa(fa_ip=public_uvm_1, auth=pe_auth, fs_uuid=fs_uuid)

  sys.exit(0)

if __name__ == '__main__':
  main()
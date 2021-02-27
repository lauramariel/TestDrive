"""
create_smb_share.py: automation to configure
existing file servers on an NX-on-GCP
cluster with an SMB share

Requires an AD server and existing FS to be 
enabled to use AD/SMB.

Updates:
2021-02-26 - Updated to support multiple File Servers. No longer
  using nutest libraries

Author:   laura@nutanix.com
Date:     2020-03-16
Updated:  2021-02-26
"""

import sys
import os
import json
import time
import requests

from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_fs_uuid(auth, ip):
  print(">>> Getting File Server UUIDs")
  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/api/nutanix/v3/groups"
  data = { "entity_type": "file_server_service" }
  print(f">>> Url: {url} Payload: {data}")
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)

  if resp.ok:
    details = resp.json()
    print(details)
    number_of_fs = details.get("filtered_entity_count")

    uuids = []
    for i in range(number_of_fs):
      uuids.append(details.get("group_results")[0].get("entity_results")[i].get("entity_id"))

    return uuids
  else:
    print(f">>> Error getting FS UUIDs: {resp.text}")

def create_shares(auth, ip, fs_uuid):
  # model for creating a share
  with open('fs_create_share.json') as f:
    sharecfg = json.load(f)
    f.close()

  # get AD config
  with open('ad_config.json') as f:
    adconfig = json.load(f)
    f.close()

  # Create SMB share
  sharecfg["name"] = "SMB_Share"
  sharecfg["windowsAdDomainName"] =  "{domain}".format(domain=adconfig.get("ad_domain_name"))
  sharecfg["protocolType"] = "SMB"
 
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/shares"
  print(f">>> Url: {url} Payload: {sharecfg}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(sharecfg), verify=False)
  print(resp)
  print(resp.text)

  # need to let the first share finish creating before adding the second one
  print(">>> Sleeping for 20s")
  time.sleep(20)

  # Create NFS share
  sharecfg["name"] = "NFS_Share"
  sharecfg["protocolType"] = "NFS"
  # delete unneeded keys
  del sharecfg["enableAccessBasedEnumeration"]
  del sharecfg["enableSmb3Encryption"]
 
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/shares"
  print(f">>> Url: {url} Payload: {sharecfg}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(sharecfg), verify=False)
  print(resp)
  print(resp.text) 

def main():
  # config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  # print(config)

  # pc_info = config.get("tdaas_pc")
  # pc_ip = pc_info.get("ips")[0][0]
  # prism_password = pc_info.get("prism_password")

  # cvm_info = config.get("tdaas_cluster")
  # cvm_ip = cvm_info.get("ips")[0][0]
  # pe_password = cvm_info.get("prism_password")

  pc_ip = "34.74.139.172"
  prism_password = 'STJeVIMN*9Y'

  cvm_ip = "34.74.251.25"
  pe_password = 'VKMOCQy2*Y'

  pe_auth = HTTPBasicAuth("admin", f"{pe_password}")
  auth = HTTPBasicAuth("admin", f"{prism_password}")

  # get list of file server UUIDs from PC groups API
  fs_uuids = get_fs_uuid(auth, pc_ip)
  print(f">>> Number of File Servers: {len(fs_uuids)} File Server UUIDs: {fs_uuids}")

  for fs_uuid in fs_uuids:
    print(f">>> Creating SMB and NFS shares on {fs_uuid}")
    create_shares(pe_auth, cvm_ip, fs_uuid)

  sys.exit(0)

if __name__ == '__main__':
  main()
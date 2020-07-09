"""
create_smb_share.py: automation to configure
the existing file server on an NX-on-GCP
cluster with an SMB share

Requires an AD server and existing FS to be 
enabled to use AD/SMB.

Author: laura@nutanix.com
Date:   2020-03-16
"""

import sys
import os
import json
import time
import requests

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_fs_uuid(cluster):
  INFO("Getting FS UUID")
  resp = cluster.execute("afs info.fileservers | grep -v [Ff]ileserver | awk {'printf $1'} | tail -1")
  INFO(resp)
  # todo: error handling
  fs_uuid = resp.get('stdout')
  return fs_uuid

def create_smb_share(ip, password, fs_uuid):
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
 
  url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers/{}/shares".format(ip, fs_uuid)
  payload = json.dumps(sharecfg)
  INFO("Url {}".format(url))
  INFO("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  INFO(resp)

  # need to let the first share finish creating before adding the second one
  time.sleep(20)

  # Create NFS share
  sharecfg["name"] = "NFS_Share"
  sharecfg["protocolType"] = "NFS"
  # delete unneeded keys
  del sharecfg["enableAccessBasedEnumeration"]
  del sharecfg["enableSmb3Encryption"]
 
  url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers/{}/shares".format(ip, fs_uuid)
  payload = json.dumps(sharecfg)
  INFO("Url {}".format(url))
  INFO("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  INFO(resp) 

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  prism_password = cvm_info.get("prism_password")
  #cvm_internal_ip = cvm_info.get("ips")[0][1]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  # get file server UUID
  fs_uuid = get_fs_uuid(cluster=cluster)
  # change file server information
  INFO("Creating SMB share on {}".format(fs_uuid))
  create_smb_share(ip=cvm_external_ip, password=prism_password, fs_uuid=fs_uuid)

if __name__ == '__main__':
  main()
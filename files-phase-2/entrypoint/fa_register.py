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

def register_fa(fa_ip, password, fs_uuid):
  # model for deploying FA
  with open('fa_register.json') as f:
    facfg = json.load(f)
    f.close()

  # AD info
  with open('ad_config.json') as f:
    adconfig = json.load(f)
    f.close()

  # Set up payload
  facfg["dns_domain_name"] = "{domain}".format(domain=adconfig.get("ad_domain_name"))
  facfg["file_server_uuid"] =  fs_uuid
  facfg["ad_credentials"]["username"] = "{ad_admin_user}".format(ad_admin_user=adconfig.get("ad_admin_user"))
  facfg["ad_credentials"]["domain"] = "{domain}".format(domain=adconfig.get("ad_domain_name"))
  facfg["ad_credentials"]["password"] = "{ad_admin_pass}".format(ad_admin_pass=adconfig.get("ad_admin_pass"))
 
  url = "https://{}:3000/fileservers/subscription?user_name=admin&file_server_uuid={}".format(fa_ip, fs_uuid)
  payload = json.dumps(facfg)
  INFO("Url {}".format(url))
  INFO("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  INFO(resp)
  INFO(resp.text)
  
  # sleep 60
  time.sleep(60)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  prism_password = cvm_info.get("prism_password")
  #cvm_internal_ip = cvm_info.get("ips")[0][1]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  proxy_vm = config.get("proxy_vm")

  # public_uvm_1 is the FA server 
  public_uvm_1 = proxy_vm["public_uvms"]["public-uvm-1"]["external_ip"]

  # get required values for payload
  INFO("Getting FS UUID")
  fs_uuid = get_fs_uuid(cluster)
  INFO("FS UUID: {}".format(fs_uuid))

  # deploy FA
  INFO("Registering file server with FA")
  register_fa(fa_ip=public_uvm_1, password=prism_password, fs_uuid=fs_uuid)

  exit(0)

if __name__ == '__main__':
  main()
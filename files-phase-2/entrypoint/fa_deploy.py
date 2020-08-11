"""
fa_deploy.py: automation to deploy File Analytics
on an NX-on-GCP cluster

Author: laura@nutanix.com
Date:   2020-07-16
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

def get_ctr_details(ip, password):
  url = "https://{}:9440/PrismGateway/services/rest/v2.0/storage_containers/?search_string=gcp-fs".format(ip)
  INFO("URL {} ".format(url))
  headers = {'Content-type': 'application/json'}
  ctr_details = requests.get(url, auth=HTTPBasicAuth("admin", password), headers=headers, verify=False)
  INFO(ctr_details)
  if ctr_details.ok:
      parsed_ctr_details = json.loads(ctr_details.content)
      ctr_uuid = str(parsed_ctr_details["entities"][0]["storage_container_uuid"])
      ctr_name = str(parsed_ctr_details["entities"][0]["name"])
  else:
      INFO("Error: Non-ok response")
      exit(1)

  return ctr_uuid, ctr_name

def get_network_uuid(cluster):
  INFO("Getting Network UUID")
  resp = cluster.execute("acli net.list | grep public-net | awk '{print $2}'")
  INFO(resp)
  # todo: error handling
  network_uuid = resp.get('stdout')
  return network_uuid

def deploy_fa(ip, password, ctr_uuid, ctr_name, network_uuid):
  # model for deploying FA
  with open('analytics_config.json') as f:
    facfg = json.load(f)
    f.close()

  # Set up payload
  facfg["container_uuid"] = ctr_uuid
  facfg["container_name"] =  ctr_name
  facfg["network"]["uuid"] = network_uuid
 
  url = "https://{}:9440/PrismGateway/services/rest/v2.0/analyticsplatform".format(ip)
  payload = json.dumps(facfg)
  INFO("Url {}".format(url))
  INFO("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  INFO(resp)
  INFO(resp.text)
  
  # wait for deployment to finish
  time.sleep(1200)

def delete_vm(cluster, vm_name):
  resp = cluster.execute('acli -y vm.delete {vm_name}'.format(vm_name=vm_name))
  INFO(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  prism_password = cvm_info.get("prism_password")
  #cvm_internal_ip = cvm_info.get("ips")[0][1]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  # get required values for payload
  INFO("Getting container UUID and name")
  ctr_uuid, ctr_name = get_ctr_details(ip=cvm_external_ip, password=prism_password)
  INFO("Container UUID: {}".format(ctr_uuid))
  INFO("Container name: {}".format(ctr_name))

  INFO("Getting network UUID")
  network_uuid = get_network_uuid(cluster=cluster)
  INFO("Network UUID: {}".format(ctr_uuid))

  # deploy FA
  INFO("Deploying FA - will take up to 10 minutes")
  deploy_fa(ip=cvm_external_ip, password=prism_password, ctr_uuid=ctr_uuid, ctr_name=ctr_name, network_uuid=network_uuid)

  # delete the sampleVM we created in fa_prep.py to work around IP address issue
  INFO("Deleting the dummy VM")
  delete_vm(cluster, "SampleVM")
  INFO("Finished!")
  exit(0)

if __name__ == '__main__':
  main()
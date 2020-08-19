"""
Test for AUTO-23813
(Add Request ID to config.json)

Author:   laura@nutanix.com
Date:     2020-08-18
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

def save_gcp_id(cluster, gcp_id):

  resp = cluster.execute("echo {} > /home/nutanix/gcp_id.txt".format(gcp_id))
  INFO(resp)
  resp = cluster.execute("cat /home/nutanix/gcp_id.txt")
  INFO(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  prism_password = cvm_info.get("prism_password")
  #cvm_internal_ip = cvm_info.get("ips")[0][1]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  
  gcp_id = config.get("request_id")
  save_gcp_id(cluster=cluster, gcp_id=gcp_id)

if __name__ == '__main__':
  main()

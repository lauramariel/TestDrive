"""
configure_filer.py: automation to configure
the existing file server on an NX-on-GCP
cluster with the appropriate AD and DNS settings.
Requires an AD to be configured.

Author: laura@nutanix.com
Date:   2020-03-13
"""

import sys
import os
import json
import time
import requests

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def get_fs_uuid(cluster):
  INFO("Getting FS UUID")
  resp = cluster.execute("afs info.fileservers | grep -v [Ff]ileserver | awk {'printf $1'} | tail -1")
  # todo: error handling
  fs_uuid = resp.get('stdout')
  return fs_uuid

def update_fs(ip, password, fs_uuid):
  # get file server config
  with open('fs_config.json') as f:
    fsconfig = json.load(f)
    f.close()

  # get AD config
  with open('ad_config.json') as f:
    adconfig = json.load(f)
    f.close()
  
  # get NTP config
  with open('ntp_dns_config.json') as f:
    ntpconfig = json.load(f)
    f.close()

  fsconfig["uuid"] = "{fs_uuid}".format(fs_uuid=fs_uuid)  
  fsconfig["dnsDomainName"] = "{domain}".format(domain=adconfig.get("ad_domain_name")) 
  fsconfig["dnsServerIpAddresses"] = ["{dns_server}".format(dns_server=adconfig.get("ad_server_ip"))]
  fsconfig["ntpServers"] = ["{ntp_server}".format(ntp_server=ntpconfig.get("ntp_server"))]

  # make the call
  url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers".format(ip)
  payload = fsconfig
  resp = requests.put(url, auth=HTTPBasicAuth("admin", password))


def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  prism_password = cvm_info.get("prism_password")
  #cvm_internal_ip = cvm_info.get("ips")[0][1]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  # get file server UUID
  fs_uuid = get_fs_uuid()
  # change file server information
  update_fs(ip=cvm_external_ip, password=prism_password fs_uuid=fs_uuid)

if __name__ == '__main__':
  main()
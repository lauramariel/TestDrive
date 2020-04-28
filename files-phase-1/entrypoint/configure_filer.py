"""
configure_filer.py: automation to configure
the existing file server on an NX-on-GCP
cluster with the appropriate AD, DNS, NTP settings
as specified in config files.

Requires an AD and existing FS to be configured.

After running this script:
- AD domain will be updated (Update > File Server Basics)
- DNS & NTP will be updated (Update > Network Configuration)
- SMB will be enabled and domain will be joined

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

def get_fs_ip(cluster):
  INFO("Getting FS IP")
  resp = cluster.execute("afs info.fileservers | grep -v -i 'Fileserver' | awk '{print $3}'")
  INFO(resp)
  # todo: error handling
  fs_ip = resp.get('stdout')
  fs_ip.strip('\r\n')
  return fs_ip

def get_fs_uuid(cluster):
  INFO("Getting FS UUID")
  resp = cluster.execute("afs info.fileservers | grep -v [Ff]ileserver | awk {'printf $1'} | tail -1")
  INFO(resp)
  # todo: error handling
  fs_uuid = resp.get('stdout')
  return fs_uuid

def update_fs(ip, password, fs_uuid):
  # model for configuring fs
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
  payload = json.dumps(fsconfig)
  INFO("Url {}".format(url))
  INFO("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.put(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  INFO(resp)

  time.sleep(30)

def enable_ad(ip, password, fs_uuid):
  # model for configuring directory services
  with open('fs_enable_ad.json') as f:
    dircfg = json.load(f)
    f.close()

  # get AD config
  with open('ad_config.json') as f:
    adconfig = json.load(f)
    f.close()

  dircfg["adDetails"]["windowsAdDomainName"] = "{domain}".format(domain=adconfig.get("ad_domain_name"))
  dircfg["adDetails"]["windowsAdUsername"] =  "{ad_admin_user}".format(ad_admin_user=adconfig.get("ad_admin_user"))
  dircfg["adDetails"]["windowsAdPassword"] = "{ad_admin_pass}".format(ad_admin_pass=adconfig.get("ad_admin_pass"))
 
  url = "https://{}:9440/PrismGateway/services/rest/v1/vfilers/{}/configureNameServices".format(ip, fs_uuid)
  payload = json.dumps(dircfg)
  INFO("Url {}".format(url))
  INFO("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  INFO(resp)

  # need to wait for about 90 seconds for completion
  time.sleep(90)

# populate fake data in FS
def populate_data(cluster, fsvm_ip):
  INFO("Copy script to FSVM, run it, and set crontab")
  #resp = cluster.execute("ssh {} 'cd /home/nutanix/minerva/bin; wget https://storage.googleapis.com/testdrive-templates/files/populate_fs_metrics.py; python populate_fs_metrics.py 24 12'".format(fsvm_ip))
  resp = cluster.execute("ssh {} 'cd /home/nutanix/minerva/bin; wget https://storage.googleapis.com/testdrive-templates/files/populate_fs_metrics.py; python populate_fs_metrics.py 24 12; (crontab -l 2>/dev/null; echo \"* */24 * * * /usr/bin/python /home/nutanix/minerva/bin/populate_fs_metrics.py 24 12\") | crontab -'".format(fsvm_ip))
  INFO(resp)
  stdout = resp.get('stdout')
  INFO(stdout)
  time.sleep(60)


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

  # get file server virtual IP
  fs_ip = get_fs_ip(cluster=cluster)

  # change file server information
  INFO("Updating FS with domain, DNS, NTP {}".format(fs_uuid))
  update_fs(ip=cvm_external_ip, password=prism_password, fs_uuid=fs_uuid)
  INFO("Enabling Directory Services")
  enable_ad(ip=cvm_external_ip, password=prism_password, fs_uuid=fs_uuid)
  INFO("Running data population script on FSVM")
  populate_data(cluster=cluster, fsvm_ip=fs_ip)

if __name__ == '__main__':
  main()
"""
configure_filer.py: automation to configure
the existing file server on an NX-on-GCP
cluster with the appropriate AD, DNS, NTP settings
as specified in config files.

Requires an AD and existing FS to be configured.

After running this script:
- PE name server will be set to AutoDC IP
- AD domain will be updated (Update > File Server Basics)
- DNS & NTP will be updated (Update > Network Configuration)
- SMB will be enabled and domain will be joined
- Data will be populated in FSVM via a script downloaded from
  a Google Bucket

Updates:
2021-02-25 - Updated to support multiple File Servers. No longer
  using nutest libraries

Author:   laura@nutanix.com
Date:     2020-03-16
Updated:  2021-02-25
"""

import sys
import os
import json
import time
import requests

from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def set_cluster_dns(auth, ip):
  # get DNS config which was set by set_ad_ip.py
  with open('ntp_dns_config.json') as f:
    dnsconfig = json.load(f)
    f.close()
  dns_addr = dnsconfig.get("dns_server")

  print(f">>> Setting Cluster DNS to {dns_addr}")

  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/cluster/name_servers/add_list"
  data = [{"ipv4": dns_addr}]

  print(f">>> Url: {url} Payload: {data}")
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)
  print(resp.text)

  if resp.ok:
    return True
  else:
    return False

def get_fs_ip(auth, ip):
  pass

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
  print("Url {}".format(url))
  print("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.put(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  print(resp)
  print(resp.text)

  time.sleep(30)

def update_dns(ip, password, fs_uuid):
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/addDns"  
  dnsconfig = { "dnsOpType": "MS_DNS", "dnsServer": "", "dnsUserName": "administrator", "dnsPassword": "nutanix/4u" }
  payload = json.dumps(dnsconfig)
  print(f">>> Url {url}")
  print(f">>> Payload {url}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  print(resp)
  print(resp.text)


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
  print("Url {}".format(url))
  print("Payload {}".format(payload))
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=payload, verify=False)
  print(resp)
  print(resp.text)

  # need to wait for about 90 seconds for completion
  time.sleep(90)

# populate fake data in FS
def populate_data(cluster, fsvm_ip):
  print("Copy script to FSVM, run it, and set crontab")
  #resp = cluster.execute("ssh {} 'cd /home/nutanix/minerva/bin; wget https://storage.googleapis.com/testdrive-templates/files/populate_fs_metrics.py; python populate_fs_metrics.py 24 12'".format(fsvm_ip))
  resp = cluster.execute("ssh {} 'cd /home/nutanix/minerva/bin; wget https://storage.googleapis.com/testdrive-templates/files/populate_fs_metrics.py; python populate_fs_metrics.py 24 12; (crontab -l 2>/dev/null; echo \"*/30 * * * * /usr/bin/python /home/nutanix/minerva/bin/populate_fs_metrics.py 24 12\") | crontab -'".format(fsvm_ip))
  print(resp)
  stdout = resp.get('stdout')
  print(stdout)
  time.sleep(60)


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

  # get file server virtual IP
  #fs_ip = get_fs_ip(auth, pc_ip)

  # change file server information
  print(">>> Setting cluster DNS")
  set_cluster_dns(pe_auth, cvm_ip)

  for fs_uuid in fs_uuids:
    print(f"Configuring FS {fs_uuid}")
    print(f"========================")
    print(f">>> Updating FS with domain, DNS, NTP")
    update_fs(ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid)
    print(">>> Update DNS with required file server entries")
    update_dns(ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid)
    print(">>> Enabling Directory Services")
    enable_ad(ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid)

  #print("Running data population script on FSVM")
  #populate_data(cluster=cluster, fsvm_ip=fs_ip)

  sys.exit(0)

if __name__ == '__main__':
  main()

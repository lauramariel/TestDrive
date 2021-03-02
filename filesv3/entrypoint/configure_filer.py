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
  with open('specs/ntp_dns_config.json') as f:
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

"""
Get FS UUID
We could get this from PE with v1 APIs /PrismGateway/services/rest/v1/vfilers
But using PC with v3 APIs /api/nutanix/v3/groups
"""
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

"""
Rename FS
Using PE v1 APIs
"""
def rename_fs(auth, ip, password, fs_uuid, role):
  # Get the file server info
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers?fs_uuid={fs_uuid}"
  print(f">>> Url: {url}")
  headers = {'Content-type': 'application/json'}
  resp = requests.get(url, auth=auth, headers=headers, verify=False)
  print(resp)

  # Get the name
  if resp.ok:
    details = resp.json()
    # GET /PrismGateway/services/rest/v1/vfilers?fs_uuid={fs_uuid}
    # doesn't seem to be returning just the data for fs_uuid
    # so let's find it
    for fs in details.get("entities"):
      if fs.get("uuid") == fs_uuid:
        fs_name = fs.get("name")
        print(f">>> Original Name: {fs_name}")
  else:
    print(f">>> Error getting File Server Name: {resp.text}")
    sys.exit(1)

  # Update the name
  # default name is gcp-fs-xxxxxxxx
  # but this will be able to be changed via the spec
  # so don't change it if it's already called primary

  if "primary" not in fs_name and "target" not in fs_name:
    fs_name_prefix = "fs"
    new_name = fs_name_prefix + "-" + role
    url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers"
    data = { "uuid": fs_uuid, "name": new_name }
    resp = requests.put(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)

    print("Sleeping 30s")
    time.sleep(30)
  else:
    print(f"FS name is already designated as primary or target, presumably via the " +
      "NX-on-GCP template spec, so not renaming")

def update_fs(auth, ip, password, fs_uuid):
  # model for configuring fs
  with open('specs/fs_config.json') as f:
    fsconfig = json.load(f)
    f.close()

  # get AD config
  with open('specs/ad_config.json') as f:
    adconfig = json.load(f)
    f.close()
  
  # get NTP config
  with open('specs/ntp_dns_config.json') as f:
    ntpconfig = json.load(f)
    f.close()

  fsconfig["uuid"] = "{fs_uuid}".format(fs_uuid=fs_uuid)  
  fsconfig["dnsDomainName"] = "{domain}".format(domain=adconfig.get("ad_domain_name")) 
  fsconfig["dnsServerIpAddresses"] = ["{dns_server}".format(dns_server=adconfig.get("ad_server_ip"))]
  fsconfig["ntpServers"] = ["{ntp_server}".format(ntp_server=ntpconfig.get("ntp_server"))]

  # make the call
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers"
  data = json.dumps(fsconfig)
  print(f">>> Url: {url} Payload: {data}")
  headers = {'Content-type': 'application/json'}
  resp = requests.put(url, auth=auth, headers=headers, data=data, verify=False)
  print(resp)
  print(resp.text)

  print("Sleeping 30s")
  time.sleep(30)

def update_dns(auth, ip, password, fs_uuid):
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/addDns"  
  dnsconfig = { "dnsOpType": "MS_DNS", "dnsServer": "", "dnsUserName": "administrator", "dnsPassword": "nutanix/4u" }
  data = json.dumps(dnsconfig)
  print(f">>> Url: {url} Payload: {data}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=auth, headers=headers, data=data, verify=False)
  print(resp)
  print(resp.text)


def enable_ad(auth, ip, password, fs_uuid):
  # model for configuring directory services
  with open('specs/fs_enable_ad.json') as f:
    dircfg = json.load(f)
    f.close()

  # get AD config
  with open('specs/ad_config.json') as f:
    adconfig = json.load(f)
    f.close()

  dircfg["adDetails"]["windowsAdDomainName"] = "{domain}".format(domain=adconfig.get("ad_domain_name"))
  dircfg["adDetails"]["windowsAdUsername"] =  "{ad_admin_user}".format(ad_admin_user=adconfig.get("ad_admin_user"))
  dircfg["adDetails"]["windowsAdPassword"] = "{ad_admin_pass}".format(ad_admin_pass=adconfig.get("ad_admin_pass"))
 
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/vfilers/{fs_uuid}/configureNameServices"
  data = json.dumps(dircfg)
  print(f">>> Url: {url} Payload: {data}")
  headers = {'Content-type': 'application/json'}
  resp = requests.post(url, auth=auth, headers=headers, data=data, verify=False)
  print(resp)
  print(resp.text)

  # need to wait for about 90 seconds for completion
  time.sleep(90)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  print(config)

  pc_info = config.get("tdaas_pc")
  pc_ip = pc_info.get("ips")[0][0]
  pc_password = pc_info.get("prism_password")

  cvm_info = config.get("tdaas_cluster")
  cvm_ip = cvm_info.get("ips")[0][0]
  pe_password = cvm_info.get("prism_password")

  # pc_ip = "34.74.139.172"
  # pc_password = 'STJeVIMN*9Y'

  # cvm_ip = "34.74.251.25"
  # pe_password = 'VKMOCQy2*Y'

  pe_auth = HTTPBasicAuth("admin", f"{pe_password}")
  auth = HTTPBasicAuth("admin", f"{pc_password}")

  # get list of file server UUIDs from PC groups API
  fs_uuids = get_fs_uuid(auth, pc_ip)
  print(f">>> Number of File Servers: {len(fs_uuids)} File Server UUIDs: {fs_uuids}")

  # get file server virtual IP
  #fs_ip = get_fs_ip(auth, pc_ip)

  # change file server information
  print(">>> Setting cluster DNS")
  set_cluster_dns(pe_auth, cvm_ip)

  fs_count = 0

  for fs_uuid in fs_uuids:
    print(f"#####################################################")
    print(f"# Configuring FS {fs_uuid} #")
    print(f"#######################################################")
    # keep track of FS count
    fs_count += 1

    # designate the first FS as primary 
    # and the second as target
    # if there's any more than 2, don't worry about those
    if (fs_count == 1):
      print(f">>> Renaming FS to primary")
      rename_fs(auth=pe_auth, ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid, role="primary")
    elif (fs_count == 2):
      print(f">>> Renaming FS to target")
      rename_fs(auth=pe_auth, ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid, role="target")

    print(f">>> Updating FS with domain, DNS, NTP")
    update_fs(auth=pe_auth, ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid)
    print(">>> Update DNS with required file server entries")
    update_dns(auth=pe_auth, ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid)
    print(">>> Enabling Directory Services")
    enable_ad(auth=pe_auth, ip=cvm_ip, password=pe_password, fs_uuid=fs_uuid)

  sys.exit(0)

if __name__ == '__main__':
  main()

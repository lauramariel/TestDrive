"""
set_ad_ip.py

After running this script:
- Set AD IP in the config used by other scripts
- Sets based on AutoDC IP. If AutoDC IP doesn't exist
- then use Cloudflare DNS 1.1.1.1

Author:   laura@nutanix.com
Date:     2020-05-08
"""

import sys
import os
import json
import pdb

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def set_ad_ip(cluster, auto_dc_vm):
  INFO("Getting AutoDC IP")
  resp = cluster.execute("acli -o json vm.get {vm_name}".format(vm_name=auto_dc_vm))
  output = json.loads(resp.get("stdout"))

  if not output["data"]:
    # no data was returned so log the error and set the IP to 1.1.1.1
    ERROR(output["error"])
    ERROR("Setting IP to 1.1.1.1")
    dns_ip = "1.1.1.1"
  else:
    # get vm_id from the acli output
    vm_id = output["data"].keys()[0]

    # assuming the first NIC IP is what we want
    dns_ip = output["data"][vm_id]["config"]["nic_list"][0]["ip_address"]

  # get config files and set the appropriate keys
  INFO("Writing {dns_ip} to config files".format(dns_ip=dns_ip))

  # Clean this up later
  f = open("ad_config.json", "r")
  adconfig = json.load(f)
  f.close()
  adconfig["ad_server_ip"] = "{dns_ip}".format(dns_ip=dns_ip)
  f = open("ad_config.json", "w")
  json.dump(adconfig, f)
  f.close()

  f = open("ntp_dns_config.json", "r")
  dnsconfig = json.load(f)
  f.close()
  dnsconfig["dns_server"] = "{dns_ip}".format(dns_ip=dns_ip)
  f = open("ntp_dns_config.json", "w")
  json.dump(dnsconfig, f)
  f.close()

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)

  auto_dc_vm = "AutoDC2"

  # set AD IP based on AutoDC VM if it exists
  set_ad_ip(cluster, auto_dc_vm)

  exit(0)

if __name__ == '__main__':
  main()
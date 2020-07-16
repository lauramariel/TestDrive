"""
update-network.py: update public-net pool range to the 
internal UVM IPs associated with an external IP (proxy VMs)

Author:   laura@nutanix.com
Date:     2020-07-16
"""

import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def update_network(cluster, start, end):
  INFO("Deleting the existing pool for network public-net")
  resp = cluster.execute("acli net.delete_dhcp_pool public-net start=10.31.0.10", timeout=300)
  INFO("Adding a new pool for network public-net")
  resp = cluster.execute("acli net.add_dhcp_pool public-net start={start} end={end}", timeout=300)
  INFO(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  # get the internal IPs that were assigned and determine what the range should be
  public_uvm_1 = config.get("public-uvm-1")
  public_uvm_2 = config.get("public-uvm-2")

  # get the last octet of the IPs and see which one is the smaller one
  uvm_1_last_octet = [ int(a) for a in public_uvm_1.get("internal_ip").split('.')][3]
  uvm_2_last_octet = [ int(a) for a in public_uvm_2.get("internal_ip").split('.')][3]

  if min(uvm_1_last_octet, uvm_2_last_octet) == uvm_1_last_octet:
      start = public_uvm_1
      end = public_uvm_2
  else:
      start = public_uvm_2
      end = public_uvm_1

  INFO("Start IP will be set to: ")
  INFO("End IP will be set to: ")


  
  # update public-net
  update_network(cluster, start, end)
  exit(0)

if __name__ == '__main__':
  main()

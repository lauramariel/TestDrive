"""
fa_prep.py: custom config for FA on NX-on-GCP

This script does the following to support File Analytics on GCP:

1. Narrows the public-net pool range to 2 internal UVM IPs 
   associated with the external IPs provided by NX-on-GCP via proxy and
   sets AutoDC IP as the DNS server for public-net.
2. Creates a VM using the second IP so when deployed, File Analytics
   will get the first IP and we can control which one it gets.
3. Downloads updated convert_image.py script to CVM (requirement from eng)

1 & 2 are to workaround the requirement that File Analytics has
to be deployed in a managed network and we are unable to define the IP
when deploying.

Author:   laura@nutanix.com
Date:     2020-07-16
"""

import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def update_network(cluster, start, end):
  INFO("Deleting the existing pool for network public-net")
  resp = cluster.execute("acli net.delete_dhcp_pool public-net start=10.31.0.10", timeout=300)
  INFO(resp)
  INFO("Adding a new pool for network public-net")
  resp = cluster.execute("acli net.add_dhcp_pool public-net start={} end={}".format(start, end), timeout=300)
  INFO(resp)
  INFO("Clearing DHCP/DNS config for network public-net")
  resp = cluster.execute("acli net.clear_dhcp_dns public-net")
  INFO(resp)
  INFO("Adding AutoDC IP as the DNS server to public-net")
  resp = cluster.execute("acli net.update_dhcp_dns public-net servers=172.31.0.41")
  INFO(resp)

def create_vm(cluster, ip):
  INFO("Creating a dummy VM on {}".format(ip))
  resp = cluster.execute('acli vm.create SampleVM')
  INFO(resp)
  time.sleep(1)
  resp = cluster.execute('acli vm.nic_create SampleVM ip={ip} network={network}'.format(ip=ip, network="public-net"))
  INFO(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  proxy_vm = config.get("proxy_vm")
  # get the internal IPs that were assigned and determine what the range should be
  public_uvm_1 = proxy_vm["public_uvms"]["public-uvm-1"]["internal_ip"]
  public_uvm_2 = proxy_vm["public_uvms"]["public-uvm-2"]["internal_ip"]

  # get the last octet of the IPs and see which one is the smaller one
  uvm_1_last_octet = [ int(a) for a in public_uvm_1.split('.')][3]
  uvm_2_last_octet = [ int(a) for a in public_uvm_2.split('.')][3]

  if min(uvm_1_last_octet, uvm_2_last_octet) == uvm_1_last_octet:
      start = public_uvm_1
      end = public_uvm_2
  else:
      start = public_uvm_2
      end = public_uvm_1

  # update public-net to narrow the range to 2 IPs
  INFO("Start IP will be set to: {}".format(start))
  INFO("End IP will be set to: {}".format(end))
  update_network(cluster, start, end)

  # create dummy VM to use one of the IPs
  INFO("Creating a dummy VM")
  create_vm(cluster=cluster, ip=public_uvm_2)

  # download the required convert_image.py script to the cluster
  INFO("Save original convert_image.py script")
  resp = cluster.execute("cp /home/nutanix/bin/convert_image.py /home/nutanix/bin/convert_image.py.orig")
  INFO("Downloading convert_image.py to CVM")
  resp = cluster.execute('cd /usr/local/nutanix/bin/; curl -kSOL https://storage.googleapis.com/testdrive-templates/files/deepdive/convert_image.py')
  INFO(resp)

  sys.exit(0)

if __name__ == '__main__':
  main()

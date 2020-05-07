"""
set_ntp_dns.py: automation to configure
NTP and DNS on an NX-on-GCP cluster and
on the default network

Author: laura@nutanix.com
Date:   2020-03-13
"""

import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.image.image import Image
from framework.interfaces.interface import Interface
from framework.entities.cluster.nos_cluster import NOSCluster

def set_ntp_server(cluster, ntp_server):
  # set NTP server on the cluster
  INFO("Setting NTP server to {ntp_server} on the cluster".
             format(ntp_server=ntp_server))
  cluster.execute('ncli cluster add-to-ntp-servers servers='
                         '{ntp_server}'.
                         format(ntp_server=ntp_server))

def set_dns_server(cluster, dns_server, network_name):
  # set DNS server on the cluster
  INFO("Setting DNS server to {dns_server} on the cluster".
             format(dns_server=dns_server))
  cluster.execute('ncli cluster add-to-name-servers servers='
                         '{dns_server}'.
                         format(dns_server=dns_server))
  # set DNS server on the network
  INFO("Setting DNS server IP to {dns_server} on {network_name}".
             format(network_name=network_name,
                           dns_server=dns_server))
  cluster.execute('acli net.update_dhcp_dns {network_name}'
                         ' servers={dns_server}'.
                         format(network_name=network_name,
                           dns_server=dns_server))

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

  INFO(config)

  cvm_info = config.get("tdaas_cluster")

  # get desired DNS and NTP settings for the cluster
  with open('ntp_dns_config.json') as f:
    config = json.load(f)
    f.close()
  ntp_server = config.get("ntp_server")
  dns_server = config.get("dns_server")

  cvm_external_ip = cvm_info.get("ips")[0][0]
  #cvm_internal_ip = cvm_info.get("ips")[0][1]

  network_name = "default-net"

  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)
  set_ntp_server(cluster=cluster,
                  ntp_server=ntp_server)
  set_dns_server(cluster=cluster,
                  dns_server=dns_server,
                  network_name=network_name)

  time.sleep(30)

if __name__ == '__main__':
  main()
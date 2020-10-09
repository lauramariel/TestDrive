"""
fa_patches.py:
- Updates ZK with the proxy URL of FA to support
direct access to File Analytics on Test Drive
- Updates minerva version to 1.1.1 to support port 443

Author:   laura@nutanix.com
Date:     2020-07-20
Updated:  2020-09-04
"""

import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

UPDATE_FA_FILE_PATH="https://storage.googleapis.com/testdrive-templates/files/deepdive/fa_update_zk.tar"
UPDATE_MINERVA_PATH="https://storage.googleapis.com/testdrive-templates/files/deepdive/nutanix-minervacvm-el7.3-release-fsm-1.1.1-stable-e4a1334b74e7b8efa6d5d342bf7cce8e478164b2-x86_64.tar.gz"
MINERVA_PACKAGE_PATH="/home/nutanix/nutanix-minervacvm-el7.3-release-fsm-1.1.1-stable-e4a1334b74e7b8efa6d5d342bf7cce8e478164b2-x86_64.tar.gz"
PRISM_FILE_PATH=""

def update_zk(cluster, ip):
  INFO("Downloading tarball to cluster to update zk node to external IP of FA")
  resp = cluster.execute("cd /home/nutanix; curl -kSOL {}".format(UPDATE_FA_FILE_PATH), timeout=300)
  INFO(resp)
  INFO("Extracting tarball")
  resp = cluster.execute("tar -xvf fa_update_zk.tar -C /tmp", timeout=60)
  INFO(resp)
  INFO("Moving scripts to appropriate dir and executing")
  resp = cluster.execute("mv /tmp/fa_update_zk/* /home/nutanix/bin/; cd /home/nutanix/bin; python fa_update_zk_node.py --avm_ip={avm_ip}".format(avm_ip=ip))
  INFO(resp)

def update_minerva(cluster):
    INFO("Downloading minerva package")
    resp = cluster.execute("cd /home/nutanix; curl -kSOL {}".format(UPDATE_MINERVA_PATH), timeout=300)
    INFO(resp)
    INFO("Upgrading minerva")
    resp = cluster.execute("upgrade_fsm.py --pkg_path={}".format(MINERVA_PACKAGE_PATH), timeout=300)
    INFO(resp)
    time.sleep(5)

def update_pc(cluster, pc_ip):
    INFO("rsync appropriate file to PC")
    resp = cluster.execute("rsync -rvz --delete --rsh=\"/usr/bin/sshpass -p \"nutanix/4u\" ssh -o StrictHostKeyChecking=no -l nutanix\" /home/nutanix/prism/webapps/console/ nutanix@{pc_ip}:/home/nutanix/prism/webapps/console/el7.3-release-euphrates-5.17.1.3-stable-7af21b92ddb92e53dd47d96347250ec4ad49a519/console/".format(pc_ip=pc_ip))
    INFO(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  pc_info = config.get("tdaas_pc")
  pc_internal_ip = pc_info.get("ips")[0][1]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  proxy_vm = config.get("proxy_vm")

  # get the external IP that was assigned that is assigned to FA
  #public_uvm_1 = proxy_vm["public_uvms"]["public-uvm-1"]["external_ip"]

  # use the url that we pass in the spec
  files_config = config.get("files-config")
  url = files_config["custom_config"]["files_url"]

  # update zookeeper with the IP
  update_zk(cluster=cluster, ip=url)

  # update minerva
  update_minerva(cluster=cluster)

  # update PC with correct file to reflect port change
  update_pc(cluster=cluster, pc_ip=pc_internal_ip)

  sys.exit(0)

if __name__ == '__main__':
  main()

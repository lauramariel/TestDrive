"""
deploy_autodc.py: automation to deploy
Alpine Linux Domain Controller on 
NX-on-GCP / Test Drive

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

def create_vm_image(cluster, name, source_url):
  """

  :param name: name the image will be uploaded as
  :param source_url: source url of image

  """
  try:
    container = 'SelfServiceContainer'
    image_type='kDiskImage'

    image = Image(cluster=cluster, interface_type=Interface.ACLI)
    image.create(name=name, image_type=image_type,
                 source_url=source_url,
                 container=container)
  except Exception as exc:
    print(exc)

def create_vm(cluster, vm_name, image_name, network_name, assigned_ip):
  """
  :param vm_name: name of the VMs. wil be appended by 1,2,3,...
  :param image_name: name of the image the vms will be created with
  """
  cluster.execute('acli vm.create {vm_name}'.
                         format(vm_name=vm_name))
  cluster.execute('acli vm.disk_create {vm_name}'
                         ' clone_from_image={image_name}'.
                         format(vm_name=vm_name, image_name=image_name))
  cluster.execute('acli vm.nic_create {vm_name}'
				  ' network={network} ip={ip}'.
						format(vm_name=vm_name, network=network_name, ip=assigned_ip))
  cluster.execute('acli vm.on {vm_name}'.
                         format(vm_name=vm_name))

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

  INFO(config)

  cvm_info = config.get("tdaas_cluster")

  cvm_external_ip = cvm_info.get("ips")[0][0]
  #cvm_internal_ip = cvm_info.get("ips")[0][1]

  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)
  create_vm_image(cluster=cluster,
                  name='AutoDC2',
                  source_url='https://storage.googleapis.com'
                             '/ntnx-td-image-repo/'
                             'AutoDC2-1360.qcow2'
                  )

  create_vm(cluster=cluster,
             vm_name='AutoDC2',
             image_name='AutoDC2',
			 network_name='default-net',
			 assigned_ip='172.31.0.201'
             )

  time.sleep(30)

if __name__ == '__main__':
  main()
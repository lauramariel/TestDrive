import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.image.image import Image
from framework.interfaces.interface import Interface
from framework.entities.cluster.nos_cluster import NOSCluster

from google.cloud import storage


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
    print exc

def create_vms(cluster, num_VMs, vm_name, image_name):
  """
  :param num_VMs: number of VMs to be created
  :param vm_name: name of the VMs. wil be appended by 1,2,3,...
  :param image_name: name of the image the vms will be created with

  """

  for num_VM in range(1,num_VMs+1):
    cluster.execute('acli vm.create {vm_name}{num}'.
                         format(num=num_VM, vm_name=vm_name))
    cluster.execute('acli vm.disk_create {vm_name}{num}'
                         ' clone_from_image={image_name}'
                         .format(num=num_VM, vm_name=vm_name, image_name=image_name))
    cluster.execute('acli vm.on {vm_name}{num}'.
                         format(num=num_VM, vm_name=vm_name))


def get_file_url(file_name):
  """
  Gets the link to the mentioned file name from nucloud-gcp-infra bucket.
  """

  creds_path = os.path.join('/', 'toolbox', 'bhishma', 'plugins', 'lib',
                            'gcp_cluster', 'nutest_gcp_creds.json')
  client = storage.Client.from_service_account_json(creds_path)
  bucket = client.bucket('nucloud-gcp-infra')
  blob = bucket.get_blob(file_name)

  return blob.generate_signed_url(int(time.time()) + 360)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

  INFO(config)

  cvm_info = config.get("tdaas_cluster")

  cvm_external_ip = cvm_info.get("ips")[0][0]
  cvm_internal_ip = cvm_info.get("ips")[0][1]

  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)
  create_vm_image(cluster=cluster,
                  name='tinycore_loadrunner',
                  source_url='https://s3.amazonaws.com'
                             '/ntnx-portal-sb/temp/demo/'
                             'TinyCoreHRApp.vdi'
                  )

  create_vms(cluster=cluster,
             num_VMs=1,
             vm_name='tinyloadrunner',
             image_name='tinycore_loadrunner'
             )

  time.sleep(30)

if __name__ == '__main__':
  main()



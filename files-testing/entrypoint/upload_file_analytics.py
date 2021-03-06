"""
upload_file_analytics.py: automation to 
configure upload File Analytics software
to a NX-on-GCP cluster

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


def download_fa(cluster, fa_url, fa_metadata_url):
  """
  """
  cluster.execute('cd /home/nutanix;'
                    'curl -kSOL {fa_url}'.
                    format(fa_url=fa_url))
  cluster.execute('curl -kSOL {fa_metadata_url}'.
                     format(fa_metadata_url=fa_metadata_url))

def upload_fa_to_cluster(cluster, fa_filepath, fa_metafilepath):
  """
  """
  cluster.execute('ncli software upload'
                    ' software-type=FILE_ANALYTICS'
                    ' file-path={fa_filepath}'
                    ' meta-file-path={fa_metafilepath}'.
                    format(fa_filepath=fa_filepath,
                      fa_metafilepath=fa_metafilepath))

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

  INFO(config)

  cvm_info = config.get("tdaas_cluster")

  cvm_external_ip = cvm_info.get("ips")[0][0]
  #cvm_internal_ip = cvm_info.get("ips")[0][1]

  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)
  INFO("Downloading File Analytics")
  download_fa(cluster=cluster,
                  fa_url='https://storage.googleapis.com'
                             '/ntnx-td-image-repo/'
                             'nutanix-file_analytics-el7.6-release-2.0.1-eafe5e9d00ee66a4356302438616004dbb387adb.qcow2',
                  fa_metadata_url='https://storage.googleapis.com'
                             '/ntnx-td-image-repo/'
                             'nutanix-file_analytics-el7.6-release-2.0.1-eafe5e9d00ee66a4356302438616004dbb387adb-metadata.json'
                  )

  INFO("Uploading File Analytics to cluster")
  upload_fa_to_cluster(cluster=cluster,
                        fa_filepath='/home/nutanix/'
                          'nutanix-file_analytics-el7.6-release-2.0.1-eafe5e9d00ee66a4356302438616004dbb387adb.qcow2',
                        fa_metafilepath='/home/nutanix/'
                          'nutanix-file_analytics-el7.6-release-2.0.1-eafe5e9d00ee66a4356302438616004dbb387adb-metadata.json')

  time.sleep(30)

if __name__ == '__main__':
  main()
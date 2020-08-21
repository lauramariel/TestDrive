"""
resolve-alerts.py: resolve and acknowledge
all alerts on an NX-on-GCP cluster using ncli

After running this script:
- All alerts should be resolved

Author:   laura@nutanix.com
Date:     2020-05-07
"""

import sys
import os
import json

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def resolve_alerts(cluster):
  INFO("Resolving all alerts")
  resp = cluster.execute("for i in `ncli alerts ls | grep ID | awk '{print $3}'`; do ncli alerts resolve ids=$i; done", timeout=300)
  INFO(resp)

def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  INFO(config)
  cvm_info = config.get("tdaas_cluster")
  cvm_external_ip = cvm_info.get("ips")[0][0]
  cluster = NOSCluster(cluster=cvm_external_ip, configured=False)  

  # resolve all alerts
  resolve_alerts(cluster)
  sys.exit(0)

if __name__ == '__main__':
  main()

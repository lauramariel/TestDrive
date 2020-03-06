import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def name_cluster(cluster, name):
    cluster.execute('ncli cluster edit-params new-name="' + name + '"')

def main():
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

    INFO(config)

    cvm_info = config.get("tdaas_cluster")

    cvm_external_ip = cvm_info.get("ips")[0][0]
    # cvm_internal_ip = cvm_info.get("ips")[0][1]

    cluster = NOSCluster(cluster=cvm_external_ip, configured=False)
    cluster_name = "MyCluster"
 
    name_cluster(cluster=cluster, name=cluster_name)

    time.sleep(30)

if __name__ == '__main__':
    main()

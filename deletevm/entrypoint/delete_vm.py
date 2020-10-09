import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

def delete_vm(cluster, name):
    INFO("Deleting VM " + name)
    resp = cluster.execute('acli -y vm.delete ' + name)
    stdout = resp.get('stdout')
    INFO("stdout: " + stdout)

def main():
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

    INFO(config)

    if "tdaas_cluster" in config:
        cvm_info = config.get("tdaas_cluster")
    elif "on-prem-cluster" in config:
        cvm_info = config.get("on-prem-cluster")
    else:
        ERROR("on-prem-cluster or tdaas_cluster does not exist in payload")
        sys.exit(1)

    cvm_info = config.get("tdaas_cluster")

    cvm_external_ip = cvm_info.get("ips")[0][0]
    # cvm_internal_ip = cvm_info.get("ips")[0][1]

    cluster = NOSCluster(cluster=cvm_external_ip, configured=False)
 
    delete_vm(cluster=cluster, name="AppVm-4")
     
    INFO("Sleeping 30 seconds")
    time.sleep(30)

if __name__ == '__main__':
    main()

import sys
import os
import json
import time

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR
from framework.entities.cluster.nos_cluster import NOSCluster

config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
INFO(config)
cvm_info = config.get("tdaas_cluster")
cvm_external_ip = cvm_info.get("ips")[0][0]
#cvm_internal_ip = cvm_info.get("ips")[0][1]
cluster = NOSCluster(cluster=cvm_external_ip, configured=False)

INFO("Getting FS UUID")
resp = cluster.execute("afs info.fileservers | grep -v [Ff]ileserver | awk {'printf $1'} | tail -1")
# todo: check if the response is empty (no file servers)
fs_uuid = resp.get('stdout')

with open('fs_config.json') as f:
  fsconfig = json.load(f)
  f.close()

# get AD config
with open('ad_config.json') as f:
  adconfig = json.load(f)
  f.close()

# get NTP config
with open('ntp_dns_config.json') as f:
  ntpconfig = json.load(f)
  f.close()

fsconfig["uuid"] = "{fs_uuid}".format(fs_uuid=fs_uuid)  
fsconfig["dnsDomainName"] = "{domain}".format(domain=adconfig.get("ad_domain_name")) 
fsconfig["dnsServerIpAddresses"] = ["{dns_server}".format(dns_server=adconfig.get("ad_server_ip"))]
fsconfig["ntpServers"] = ["{ntp_server}".format(ntp_server=ntpconfig.get("ntp_server"))]
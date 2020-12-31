# 12/30/20 Not done

import sys
import os
import json
import requests

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR

def enable_calm(pc_external_ip, pc_password):
	# url = f"https://{pc_external_ip}:9440/api/nutanix/v3/search/favorites"
	# payload = {
	# 	"complete_query": "Calm",
	# 	"route": "calm"
	# }
    # headers = { "Content-type": "application/json" }
	# resp = requests.post(url, auth=HTTPBasicAuth("admin", pc_password), headers=headers, data=json.dumps(payload), verify=False)
	# print(resp)
	return

def main():
	# Get and log the config from the Env variable
	config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
	INFO(config)

	# Get PC info from the config dict
	pc_info = config.get("tdaas_pc")
	pc_external_ip = pc_info.get("ips")[0][0]
	#pc_internal_ip = pc_info.get("ips")[0][1]
	pc_password = pc_info.get("prism_password")

	# set required variables for request
	auth = HTTPBasicAuth("admin", pc_password)
	headers = {'Content-type': 'application/json'}

	enable_calm(pc_external_ip, pc_password)

if __name__ == "__main__":
	main()

import sys
import os
import json
import requests

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

from framework.lib.nulog import INFO, ERROR

def mark_calm_as_favorite(pc_ip, auth, headers):
	url = "https://{}:9440/api/nutanix/v3/search/favorites".format(pc_ip)
	payload = {
		"complete_query": "Calm",
		"route": "calm"
	}

	resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(payload), verify=False)
	print(resp)

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

	mark_calm_as_favorite(pc_external_ip, auth, headers)

if __name__ == "__main__":
	main()

# Accept EULA and Enable Pulse on PC

import sys
import os
import json
import requests

from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

sys.path.append(os.path.join(os.getcwd(), "nutest_gcp.egg"))

def accept_eula(pc_external_ip, pc_password):
    url = f"https://{pc_external_ip}:9440/PrismGateway/services/rest/v1/eulas/accept"
    payload = {
        "username": "Laura",
        "companyName": "Nutanix",
        "jobTitle": "TME"
    }
    headers = { "Content-type": "application/json" }
    resp = requests.post(url, auth=HTTPBasicAuth("admin", pc_password), headers=headers, data=json.dumps(payload), verify=False)
    print(resp)

def enable_pulse(pc_external_ip, pc_password):
    url = f"https://{pc_external_ip}:9440/PrismGateway/services/rest/v1/pulse"

    payload = {
        "enable": "true",
        "enableDefaultNutanixEmail": "true",
        "isPulsePromptNeeded": "false",
    }

    headers = { "Content-type": "application/json" }
    resp = requests.put(url, auth=HTTPBasicAuth("admin", pc_password), headers=headers, data=json.dumps(payload), verify=False)
    print(resp)

def main():
    # Get and log the config from the Env variable
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)

    # Get PC info from the config dict
    pc_info = config.get("tdaas_pc")
    pc_external_ip = pc_info.get("ips")[0][0]
    #pc_internal_ip = pc_info.get("ips")[0][1]
    pc_password = pc_info.get("prism_password")

    accept_eula(pc_external_ip, pc_password)
    enable_pulse(pc_external_ip, pc_password)

if __name__ == "__main__":
    main()

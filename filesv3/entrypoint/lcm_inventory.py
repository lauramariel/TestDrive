"""
lcm_inventory.py: Perform LCM Inventory on PC 2020.11 (LCM 2.1)
This uses the v1 APIs for updating LCM framework to 2.4.x

Author:   laura@nutanix.com
Date:     2021-02-24
"""

import os
import time
import sys
import json
import requests
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# def task_check(auth, ip, headers, task_uuid, success_msg):
#   task_url = f"https://{ip}:9440/api/nutanix/v3/tasks/" + task_uuid
#   for _ in range(60):
#     time.sleep(30)
#     task_resp = requests.get(task_url, auth=auth, headers=headers, verify=False)
#     if task_resp.ok:
#         task_dict = json.loads(task_resp.content)
#         print("Task status: " + task_dict["status"])
#         if task_dict["status"] == "SUCCEEDED":
#           print(success_msg)
#           sys.exit(0)
#     else:
#         print("Task_resp call failed" + json.dumps(json.loads(task_resp.content),indent=4))

def lcm_inventory(auth, ip):
  success_msg = "LCM Inventory Complete."
  headers = {'Content-Type': 'application/json'}
  url = f"https://{ip}:9440/PrismGateway/services/rest/v1/genesis"
  data = { "value": "{\".oid\":\"LifeCycleManager\",\".method\":\"lcm_framework_rpc\",\".kwargs\":{\"method_class\":\"LcmFramework\",\"method\":\"perform_inventory\",\"args\":[\"http://download.nutanix.com/lcm/2.0\"]}}" }
  resp = requests.post(url, auth=auth, headers=headers, data=json.dumps(data), verify=False)
  print(resp)

  # Check Task Status
  if resp.ok:
    task_uuid = json.loads(resp.content)["value"].split(": ")[1].strip("}").strip('"')
    print("LCM Perform Inventory Task Started." + json.dumps(json.loads(resp.content), indent=4))
    print("LCM Task: " + task_uuid)
    #task_check(auth, ip, headers, task_uuid, success_msg)
    
  # If the LCM call failed
  else:
    print("LCM Perform Inventory failed." + json.dumps(json.loads(resp.content), indent=4))


def main():
  config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
  pc_info = config.get("tdaas_pc")
  pc_ip = pc_info.get("ips")[0][0]
  prism_password = pc_info.get("prism_password")

  # pc_ip="34.74.125.248"
  # prism_password='CT1Y49HiW!BS8'

  auth = HTTPBasicAuth("admin", f"{prism_password}")

  lcm_inventory(auth, pc_ip)

if __name__ == '__main__':
  main()

# Script to upload images for TD2:
# UbuntuDesktop1604
# AutoDC2
# CentOS cloud image

import requests
import json
import os
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def upload_image(image_name, image_desc, image_url, pc_external_ip, pc_password):
        print(f"Uploading image {image_name} to {pc_external_ip}...")

        url = f"https://{pc_external_ip}:9440/api/nutanix/v3/images"

        payload = {
            "spec": {
            "name": f"{image_name}",
            "description": f"{image_desc}",
            "resources": {
            "image_type": "DISK_IMAGE",
            "source_uri": f"{image_url}"
            }
        },
            "metadata": {
                "kind": "image"
            }
        }

        print("Payload: " + json.dumps(payload))
        headers = {'Content-type': 'application/json'}
        resp = requests.post(url, auth=HTTPBasicAuth("admin", pc_password), headers=headers, data=json.dumps(payload), verify=False)
        print(f"Response: {resp}")
        print(f"Response Details: {resp.text}")

def main():

    # Get and log the config from the Env variable
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)

    # Get PC info from the config dict
    pc_info = config.get("tdaas_pc")
    pc_external_ip = pc_info.get("ips")[0][0]
    #pc_internal_ip = pc_info.get("ips")[0][1]
    pc_password = pc_info.get("prism_password")

    with open('specs/upload_image_list.json') as f:
        image_list = json.load(f)
        f.close()

    for image in image_list["images"]:
        print(f"{image}")
        upload_image(image.get("name"), image.get("desc"), image.get("url"), pc_external_ip, pc_password)
    
if __name__ == '__main__':
    main()
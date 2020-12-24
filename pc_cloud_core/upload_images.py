# Script to upload images for TD2:
# UbuntuDesktop1604
# AutoDC2

import requests
import json
import config
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

ip=config.IP
password=config.PASSWORD

def upload_image(image_name, image_desc, image_url):
        url = f"https://{ip}:9440/api/nutanix/v3/images"

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
        resp = requests.post(url, auth=HTTPBasicAuth("admin", password), headers=headers, data=json.dumps(payload), verify=False)
        print(f"Response: {resp}")
        print(f"Response Details: {resp.text}")

def main():
    images=[{"name": "UbuntuDesktop1604", "desc": "UbuntuDesktop1604", "url": "https://storage.googleapis.com/ntnx-td-image-repo/UbuntuDesktop1604-1360.qcow2"},
            {"name": "AutoDC2", "desc": "AutoDC2", "url": "https://storage.googleapis.com/ntnx-td-image-repo/AutoDC2-1360.qcow2"},
            {"name": "CentOS-7-x86_64-1810", "CentOS Cloud Image": "AutoDC2", "url": "http://download.nutanix.com/calm/CentOS-7-x86_64-1810.qcow2"}]

    for image in images:
        print(f"{image}")
        upload_image(image.get("name"), image.get("desc"), image.get("url"))
    
if __name__ == '__main__':
    main()
"""
pc_ssh_keys.py: automation to configure PC with an SSH Key
for passwordless SSH on NX-on-GCP / Test Drive.

Author: michael@nutanix.com
Date:   2020-04-16
"""

import sys
import os
import json
import traceback

from helpers.rest import RequestResponse
from helpers.calm import file_to_string, create_via_v1_post


def main():

    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)

    cvm_info = config.get("tdaas_cluster")
    pe_ip = cvm_info.get("ips")[0][0]
    pe_password = cvm_info.get("prism_password")

    # pe_ip = "34.74.251.25"
    # pe_password = 'VKMOCQy2*Y'

    try:

        # Read in our public key and create our payload
        public_key = file_to_string("/root/.ssh/id_rsa.pub")
        #public_key = file_to_string("/Users/laura.jordana/.ssh/id_rsa.pub")
        
        print(f"public_key: {public_key}")
        payload = {"name": "plugin-runner", "key": public_key}

        # Make API call to configure the authconfig
        resp = create_via_v1_post(
            pe_ip, "cluster/public_keys", pe_password, payload,
        )

        # Log appropriately based on response
        if resp.code == 200 or resp.code == 202:
            print("SSH Key added to PE successfully.")
        else:
            raise Exception(
                f"SSH Key failed to add to PE with:\n"
                + f"Resp: {resp}\n"
                + f"Error Code: {resp.code}\n"
                + f"Error Message: {resp.message}"
            )

    except Exception as ex:
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()


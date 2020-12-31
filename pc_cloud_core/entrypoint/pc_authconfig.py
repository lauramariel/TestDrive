"""
pc_authconfig.py: automation to configure AutoDC as
an Authconfig on NX-on-GCP / Test Drive.

Author: michael@nutanix.com
Date:   2020-03-30
"""

import sys
import os
import json
import traceback

from helpers.rest import RequestResponse
from helpers.calm import file_to_dict, create_via_v1_post


def main():

    # Get and log the config from the Env variable
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)

    # Get PC info from the config dict
    pc_info = config.get("tdaas_pc")
    pc_external_ip = pc_info.get("ips")[0][0]
    pc_internal_ip = pc_info.get("ips")[0][1]
    pc_password = pc_info.get("prism_password")

    try:

        # Read in our spec file
        autodc_spec = file_to_dict("specs/pc_autodc.json")
        print(f"autodc_spec: {autodc_spec}")

        # Make API call to configure the authconfig
        resp = create_via_v1_post(
            pc_external_ip, "authconfig/directories", pc_password, autodc_spec
        )

        # Log appropriately based on response
        if resp.code == 200 or resp.code == 202:
            print("Authconfig configured successfully.")
        else:
            raise Exception(
                f"Authconfig failed with:\n"
                + f"Resp: {resp}\n"
                + f"Error Code: {resp.code}\n"
                + f"Error Message: {resp.message}"
            )

    except Exception as ex:
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()


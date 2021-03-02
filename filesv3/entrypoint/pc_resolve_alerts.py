"""
pc_resolve_alerts.py: automation to resolve all alerts
in PC on NX-on-GCP / Test Drive.

Author: michael@nutanix.com
Date:   2020-06-25
"""

import sys
import os
import json
import uuid
import traceback

from helpers.rest import RequestResponse
from helpers.calm import (
    body_via_v3_post,
    create_via_v3_post,
)


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

        # Get marketplace items
        alerts = body_via_v3_post(
            pc_external_ip, "alerts", pc_password, {"length": 500}
        ).json

        # Create our alert array
        alert_array = []

        # Loop through our items
        for alert in alerts["entities"]:

            # We only care about those not resoved
            if not alert["status"]["resources"]["acknowledged_status"]["is_true"]:

                # Add the alert to the array
                alert_array.append(alert["metadata"]["uuid"])

        # Now resolve the alerts
        resp = create_via_v3_post(
            pc_external_ip,
            "alerts/action/RESOLVE",
            pc_password,
            {"alert_uuid_list": alert_array},
        )

        # Log appropriately based on response
        if resp.code == 200 or resp.code == 202:
            print(f"Alerts {alert_array} resolved successfully.")
        else:
            raise Exception(
                f"Alerts {alert_array} resolve failed with:\n"
                + f"Resp: {resp}\n"
                + f"Error Code: {resp.code}\n"
                + f"Error Message: {resp.message}"
            )

    except Exception as ex:
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

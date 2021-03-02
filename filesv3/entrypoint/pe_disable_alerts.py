"""
pe_disable_alerts.py: automation to disable alerts /
health checks on PE on NX-on-GCP / Test Drive.

Author: michael@nutanix.com
Date:   2020-07-15
"""

import sys
import os
import json
import traceback

from helpers.rest import RequestResponse
from helpers.calm import (
    file_to_dict,
    body_via_v1_get,
    update_via_v1_put,
)


def main(cluster):

    # Get and log the config from the Env variable
    config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])
    print(config)

    # Get PE info from the config dict
    pe_info = config.get(cluster)
    pe_external_ip = pe_info.get("ips")[0][0]
    pe_internal_ip = pe_info.get("ips")[0][1]
    pe_password = pe_info.get("prism_password")

    try:

        # Read in our spec file
        alert_spec = file_to_dict("specs/pe_disable_alerts.json")
        print(f"alert_spec: {alert_spec}")

        # Loop through the alert_spec
        for alert in alert_spec["entities"]:

            # Make API call to get alert info
            alert_body = body_via_v1_get(
                pe_external_ip, "health_checks", pe_password, alert
            ).json

            # Modify body for update
            alert_body["enabled"] = False

            # Make the globalConfig API call
            resp = update_via_v1_put(
                pe_external_ip, "health_checks", pe_password, "", alert_body,
            )

            # Log appropriately based on response
            if resp.code == 200 or resp.code == 202:
                print(f"Alert ID {alert} disabled successfully.")
            else:
                # We don't actually want deployments to fail, so just print
                print(
                    f"Alert ID {alert} disable failed with:\n"
                    + f"Resp: {resp}\n"
                    + f"Error Code: {resp.code}\n"
                    + f"Error Message: {resp.message}"
                )

    except Exception as ex:
        print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    for cluster in sys.argv:
        if not cluster.endswith("py"):
            main(cluster)


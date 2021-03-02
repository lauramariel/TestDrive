"""
pe_resolve_alerts.py: automation to resolve all alerts
in PE on NX-on-GCP / Test Drive.

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
    create_via_v1_post,
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

        # Get marketplace items
        alerts = body_via_v3_post(
            pe_external_ip, "alerts", pe_password, {"length": 500}
        ).json

        # Loop through our items
        for alert in alerts["entities"]:

            # We only care about those not resoved
            if not alert["status"]["resources"]["acknowledged_status"]["is_true"]:

                # Now resolve the alert
                resp = create_via_v1_post(
                    pe_external_ip,
                    f"alerts/{alert['metadata']['uuid']}/resolve",
                    pe_password,
                    None,
                )

                # Log appropriately based on response
                if resp.code == 200 or resp.code == 202:
                    print(f"Alert {alert['metadata']['uuid']} resolved successfully.")
                else:
                    raise Exception(
                        f"Alert {alert} resolve failed with:\n"
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

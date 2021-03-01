"""
upload_fa.py: automation to 
configure upload File Analytics software
to a NX-on-GCP cluster

Updates:
2021-02-28 - Move to python3, no longer using nutest libraries

Author:     laura@nutanix.com
Date:       2020-03-13
Updated:    2021-02-28
"""

import sys
import os
import json
import time

def download_fa(cluster, fa_url, fa_metadata_url):
    resp = cluster.execute(
        "cd /home/nutanix;" "curl -kSOL {fa_url}".format(fa_url=fa_url)
    )
    INFO(resp)
    resp = cluster.execute(
        "curl -kSOL {fa_metadata_url}".format(fa_metadata_url=fa_metadata_url)
    )
    INFO(resp)


def upload_fa_to_cluster(cluster, fa_filepath, fa_metafilepath):
    resp = cluster.execute(
        "ncli software upload"
        " software-type=FILE_ANALYTICS"
        " file-path={fa_filepath}"
        " meta-file-path={fa_metafilepath}".format(
            fa_filepath=fa_filepath, fa_metafilepath=fa_metafilepath
        ),
        timeout=1200,
    )
    INFO(resp)
    # todo: check for failed upload


def main():
    #config = json.loads(os.environ["CUSTOM_SCRIPT_CONFIG"])

    INFO(config)

    #cvm_info = config.get("tdaas_cluster")

    #cvm_external_ip = cvm_info.get("ips")[0][0]
    # cvm_internal_ip = cvm_info.get("ips")[0][1]

    cvm_ip = "34.74.251.25"
    pe_password = 'VKMOCQy2*Y'

    cluster = NOSCluster(cluster=cvm_ip, configured=False)
    INFO("Downloading File Analytics")
    download_fa(
        cluster=cluster,
        fa_url="https://storage.googleapis.com"
        "/ntnx-td-image-repo/"
        "nutanix-file_analytics-el7.7-release-3.0.0-b82e5ac858f94df4b7b35fb4466f3e2392e4253f.qcow2",
        fa_metadata_url="https://storage.googleapis.com"
        "/ntnx-td-image-repo/"
        "nutanix-file_analytics-el7.7-release-3.0.0-b82e5ac858f94df4b7b35fb4466f3e2392e4253f-metadata.json",
    )

    INFO("Uploading File Analytics to cluster")
    upload_fa_to_cluster(
        cluster=cluster,
        fa_filepath="/home/nutanix/"
        "nutanix-file_analytics-el7.7-release-3.0.0-b82e5ac858f94df4b7b35fb4466f3e2392e4253f.qcow2",
        fa_metafilepath="/home/nutanix/"
        "nutanix-file_analytics-el7.7-release-3.0.0-b82e5ac858f94df4b7b35fb4466f3e2392e4253f-metadata.json",
    )

    time.sleep(30)
    sys.exit(0)


if __name__ == "__main__":
    main()

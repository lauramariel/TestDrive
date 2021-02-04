"""
helpers/calm.py: Common functions to enable Calm API based
automation for NX-on-GCP.

Author: michael@nutanix.com
Date:   2020-02-24
"""

from helpers.rest import RequestParameters, RequestResponse, RESTClient
import sys
import os
import requests
import urllib3
import json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def file_to_string(filename):
    """Given a filename, return a str of the file's contents"""
    with open(os.path.join(os.getcwd(), filename)) as str_file:
        return str_file.read().rstrip("\n")


def file_to_dict(filename):
    """Given a filename, return a dict of the file's contents"""
    with open(os.path.join(os.getcwd(), filename)) as json_file:
        return json.load(json_file)


def create_v3_url(ip, endpoint):
    """Given an IP and Endpoint, return Nutanix v3 API URL"""
    return f"https://{ip}:9440/api/nutanix/v3/{endpoint}"


def create_v1_url(ip, endpoint):
    """Given an IP and  Endpoint, return Nutanix v1 API URL"""
    return f"https://{ip}:9440/PrismGateway/services/rest/v1/{endpoint}"


def recursive_dict_lookup(dictionary, array):
    """Given a dictionary, and an array of dictionary keys, return the
       corresponding value of the dictionary"""
    key = array.pop(0)
    if len(array) > 0:
        return recursive_dict_lookup(dictionary[key], array)
    else:
        return dictionary[key]


def create_proxy_array(public_uvms):
    """Given a Proxy VM dictionary, return an array of tuples"""

    uvm_array = []
    for uvm in public_uvms["public_uvms"]:
        uvm_array.append(
            (
                public_uvms["public_uvms"][uvm]["external_ip"],
                public_uvms["public_uvms"][uvm]["internal_ip"],
            )
        )
    return uvm_array


def create_via_v1_post(ip, endpoint, password, body):
    """Create a new entity via a v1 post call, return the response"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v1_url(ip, f"{endpoint}"),
        username="admin",
        password=password,
        method="post",
        payload=json.dumps(body),
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"create_via_v1_post: {ip}, {endpoint}")

    return resp


def create_via_v3_post(ip, endpoint, password, body):
    """Create a new entity via a v3 post call, return the response"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, f"{endpoint}"),
        username="admin",
        password=password,
        method="post",
        payload=json.dumps(body),
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"create_via_v3_post: {ip}, {endpoint}")

    return resp


def upload_bp_via_v3_post(ip, password, body, filename):
    """Uploads a named blueprint to a particular project"""

    # Create the file dictionary
    files = {"file": open(f"blueprints/{filename}", "rb")}

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, "blueprints/import_file"),
        username="admin",
        password=password,
        method="post",
        payload=body,
        files=files,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"upload_bp_via_v3_post: {ip}, {body}")

    return resp


def upload_icon_via_v3_post(ip, password, body, icon):
    """Uploads an app_icon"""

    # Create the file dictionary
    files = {"image": (icon["name"], open(f"images/{icon['file']}", "rb"), "image/png")}

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, "app_icons/upload"),
        username="admin",
        password=password,
        method="post",
        payload=body,
        files=files,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"upload_icon_via_v3_post: {ip}, {body}")

    return resp


def uuid_via_v3_post(ip, endpoint, password, entity_name):
    """Return the UUID of a desired entity.  If entity_name is empty
     assume a single entity in response and send first UUID"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, f"{endpoint}/list"),
        username="admin",
        password=password,
        method="post",
        payload='{"length": 100}',
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"uuid_via_v3_post: {ip}, {endpoint}, {entity_name}")

    # Return UUID
    for entity in resp.json["entities"]:
        if entity_name == "":
            return entity["metadata"]["uuid"]
        elif entity["status"]["name"] == entity_name:
            return entity["metadata"]["uuid"]


def body_via_v3_post(ip, endpoint, password, payload):
    """Return the body of a group of entities
     If payload is None, assume length=100"""

    # Determine payload
    if payload is None:
        payload = {"length": 100}

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, f"{endpoint}/list"),
        username="admin",
        password=password,
        method="post",
        payload=json.dumps(payload),
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"body_via_v3_post: {ip}, {endpoint}")

    # Return the response
    return resp


def body_via_v3_get(ip, endpoint, password, entity_uuid):
    """Return the body of a desired entity"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, f"{endpoint}/{entity_uuid}"),
        username="admin",
        password=password,
        method="get",
        payload=None,
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"body_via_v3_get: {ip}, {endpoint}, {entity_uuid}")

    # Return the response
    return resp


def update_via_v3_put(ip, endpoint, password, entity_uuid, body):
    """Update a given entity with a PUT"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, f"{endpoint}/{entity_uuid}"),
        username="admin",
        password=password,
        method="put",
        payload=json.dumps(body),
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"update_via_v3_put: {ip}, {endpoint}, {entity_uuid}")

    # Return the response
    return resp


def update_via_v1_put(ip, endpoint, password, entity, body):
    """Update a given entity with a PUT"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v1_url(ip, f"{endpoint}/{entity}"),
        username="admin",
        password=password,
        method="put",
        payload=json.dumps(body),
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"update_via_v1_put: {ip}, {endpoint}, {entity}")

    # Return the response
    return resp


def del_via_v3_delete(ip, endpoint, password, entity_uuid):
    """Delete a given entity with a DELETE"""

    # Make the API call
    parameters = RequestParameters(
        uri=create_v3_url(ip, f"{endpoint}/{entity_uuid}"),
        username="admin",
        password=password,
        method="delete",
        payload=None,
        files=None,
    )
    rest_client = RESTClient(parameters)
    resp = rest_client.request()
    print(f"del_via_v3_delete: {ip}, {endpoint}, {entity_uuid}")

    # Return the response
    return resp


def get_subnet_info(ip, password, vlan_id):
    """Given a VLAN ID, return a dict of the matching Subnet UUID and name"""

    subnet_info = {}

    # Get our subnet info from the infra
    subnets_body = body_via_v3_post(ip, "subnets", password, None)
    for subnet in subnets_body.json["entities"]:
        if subnet["spec"]["resources"]["vlan_id"] == vlan_id:
            subnet_info["name"] = subnet["spec"]["name"]
            subnet_info["uuid"] = subnet["metadata"]["uuid"]

    return subnet_info

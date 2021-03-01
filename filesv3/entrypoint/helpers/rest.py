"""
rest.py: Rest API helper classes
"""

import requests
import urllib3
import argparse
import getpass
import json

from base64 import b64encode
from requests.auth import HTTPBasicAuth


class RequestParameters:
    """
  Class to hold the parameters of our Request
  """

    def __init__(self, uri, username, password, method, payload, files):
        self.uri = uri
        self.username = username
        self.password = password
        self.method = method
        self.payload = payload
        self.files = files

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"uri={self.uri},"
            f"username={self.username},"
            f"password={self.password},"
            f"method={self.method},"
            f"payload={self.payload}"
            f"files={self.files})"
        )


class RequestResponse:
    """
  Class to hold the response from our Request
  """

    def __init__(self):
        self.code = 0
        self.message = ""
        self.json = ""
        self.details = ""

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"code={self.code},"
            f"message={self.message},"
            f"json={self.json},"
            f"details={self.details})"
        )


class RESTClient:
    """
  the RESTClient class carries out the actual API request
  by 'packaging' these functions into a dedicated class
  """

    def __init__(self, parameters: RequestParameters):
        self.params = parameters

    def request(self):
        """
    this is the main method that carries out the request
    basic exception handling is managed here, as well as
    returning the response (success or fail), as an instance
    of our RequestResponse
    """
        response = RequestResponse()
        """
    setup the HTTP Basic Authorization header based on the
    supplied username and password
    """
        username = self.params.username
        password = self.params.password
        method = self.params.method
        encoded_credentials = b64encode(
            bytes(f"{username}:{password}", encoding="ascii")
        ).decode("ascii")
        auth_header = f"Basic {encoded_credentials}"

        # Create the headers with the previous creds
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"{auth_header}",
            "cache-control": "no-cache",
        }

        try:

            # based on the method, submit the request
            if method.lower() == "post":
                if self.params.files is not None:
                    del headers["Accept"]
                    del headers["Content-Type"]
                    api_request = requests.post(
                        self.params.uri,
                        data=self.params.payload,
                        files=self.params.files,
                        headers=headers,
                        verify=False,
                        timeout=10,
                    )
                else:
                    api_request = requests.post(
                        self.params.uri,
                        data=self.params.payload,
                        headers=headers,
                        verify=False,
                        timeout=10,
                    )
            elif method.lower() == "put":
                if self.params.payload is not None:
                    api_request = requests.put(
                        self.params.uri,
                        data=self.params.payload,
                        headers=headers,
                        verify=False,
                        timeout=10,
                    )
                else:
                    api_request = requests.put(
                        self.params.uri, headers=headers, verify=False, timeout=10,
                    )
            elif method.lower() == "get":
                api_request = requests.get(
                    self.params.uri, headers=headers, timeout=10, verify=False
                )
            elif method.lower() == "delete":
                api_request = requests.delete(
                    self.params.uri, headers=headers, timeout=10, verify=False
                )
            else:
                raise Exception(
                    f"Passed method of '{method}' is not supported. "
                    + " Supported methods are 'post', 'put', 'get', and 'delete'."
                )

            # if no exceptions occur here, we can process the response
            response.code = api_request.status_code
            response.message = "Request submitted successfully."
            response.json = api_request.json()
            response.details = "N/A"
        except ValueError:
            # handle when our APIs do not return a JSON body
            response.code = api_request.status_code
            response.message = "Request submitted successfully."
            response.details = "N/A"
        except requests.exceptions.ConnectTimeout:
            # timeout while connecting to the specified IP address or FQDN
            response.code = -99
            response.message = f"Connection has timed out. {username} " + f"{password}"
            response.details = "Exception: requests.exceptions.ConnectTimeout"
        except urllib3.exceptions.ConnectTimeoutError:
            # timeout while connecting to the specified IP address or FQDN
            response.code = -99
            response.message = f"Connection has timed out."
            response.details = "urllib3.exceptions.ConnectTimeoutError"
        except requests.exceptions.MissingSchema:
            # potentially bad URL
            response.code = -99
            response.message = "Missing URL schema/bad URL."
            response.details = "N/A"
        except Exception as _e:
            # unhandled exceptions
            response.code = -99
            response.message = "An unhandled exception has occurred."
            response.details = _e

        return response

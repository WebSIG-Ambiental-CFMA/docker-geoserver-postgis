import json

import requests
from requests.auth import HTTPBasicAuth

geoserver_rest_url = "http://172.18.0.3:8080/geoserver/rest/"
geoserver_auth = HTTPBasicAuth("admin","password")

def get_all_workspace_names():
    response = requests.get(geoserver_rest_url + "workspaces",
                            auth = geoserver_auth)

    response_json_dict = json.loads(response.content)

    workspace_data_list = response_json_dict['workspaces']["workspace"]

    return [ws['name'] for ws in workspace_data_list]

def create_workspace(workspace_name):
    xml_payload = "<workspace><name>" + workspace_name + "</name></workspace>"

    response = requests.post(geoserver_rest_url + "workspaces", xml_payload,
                             headers = {"Content-type": "text/xml"},
                             auth = geoserver_auth)

    return response.status_code

def create_workspace_if_not_found(workspace_name):
    if workspace_name not in get_all_workspace_names():
        create_workspace(workspace_name)

        return True
    return False

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

def create_xml_tag(name, content):
    opening_tag = "<"  + name + ">"
    closing_tag = "</" + name + ">"

    return opening_tag + content + closing_tag

def create_workspace(workspace_name):
    xml_payload = create_xml_tag("workspace",
                                 create_xml_tag("name", workspace_name))

    response = requests.post(geoserver_rest_url + "workspaces", xml_payload,
                             headers = {"Content-type": "text/xml"},
                             auth = geoserver_auth)

    return response.status_code

def create_workspace_if_not_found(workspace_name):
    if workspace_name not in get_all_workspace_names():
        status_code = create_workspace(workspace_name)

        return status_code == 201
    return False

def create_database_xml_payload(name, host, port, user, password):
    name_tag     = create_xml_tag("name", name)
    host_tag     = create_xml_tag("host", host)
    port_tag     = create_xml_tag("port", port)
    database_tag = create_xml_tag("database", name)
    user_tag     = create_xml_tag("user", user)
    passwd_tag   = create_xml_tag("passwd", password)
    dbtype_tag   = create_xml_tag("dbtype", "postgis")

    connection_parameters_tag = create_xml_tag("connectionParameters",
                                               host_tag +
                                               port_tag +
                                               database_tag +
                                               user_tag +
                                               passwd_tag +
                                               dbtype_tag)

    data_store_tag = create_xml_tag("dataStore",
                                    name_tag + connection_parameters_tag)

    return data_store_tag

def get_all_data_store_names_from_workspace(workspace_name):
    if workspace_name not in get_all_workspace_names():
        return []

    response = requests.get(geoserver_rest_url + "workspaces/" + workspace_name + "/datastores",
                            auth = geoserver_auth)

    response_json_dict = json.loads(response.content)
    data_store_data_dict = response_json_dict['dataStores']

    if type(data_store_data_dict) is dict:
        data_store_data_list = data_store_data_dict['dataStore']

        return [ds['name'] for ds in data_store_data_list]
    else:
        return []


def create_database_store_into_workspace(workspace_name,
                                         db_name,
                                         db_host,
                                         db_port,
                                         db_user,
                                         db_password):
    xml_payload = create_database_xml_payload(name=db_name,
                                              host=db_host,
                                              port=db_port,
                                              user=db_user,
                                              password=db_password)

    response = requests.post(geoserver_rest_url + "workspaces/" + workspace_name + "/datastores",
                             xml_payload,
                             headers = {"Content-type": "text/xml"},
                             auth = geoserver_auth)

    return response.status_code

def create_database_store_into_workspace_if_not_found(workspace_name,
                                                      db_name,
                                                      db_host,
                                                      db_port,
                                                      db_user,
                                                      db_password):
    if workspace_name not in get_all_workspace_names():
        return False
    if db_name in get_all_data_store_names_from_workspace(workspace_name):
        return False
    status_code = create_database_store_into_workspace(workspace_name=workspace_name,
                                                       db_name=db_name,
                                                       db_host=db_host,
                                                       db_port=db_port,
                                                       db_user=db_user,
                                                       db_password=db_password)

    return status_code == 201

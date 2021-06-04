from typing import List
import json

import requests
from requests.auth import HTTPBasicAuth

class geoserver_connection:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.url = "http://" + host + ":" + port + "/geoserver/rest/"
        self.auth = HTTPBasicAuth(username, password)

    def get_url(self) -> str:
        return self.url

    def get_auth(self) -> HTTPBasicAuth:
        return self.auth

def get_all_workspace_names(conn: geoserver_connection) -> List[str]:
    response = requests.get(conn.get_url() + "workspaces",
                            auth = conn.get_auth())

    response_json_dict = json.loads(response.content)

    workspace_data_list = response_json_dict['workspaces']["workspace"]

    return [ws['name'] for ws in workspace_data_list]

def create_xml_tag(name: str, content: str) -> str:
    opening_tag = "<"  + name + ">"
    closing_tag = "</" + name + ">"

    return opening_tag + content + closing_tag

def create_workspace(conn: geoserver_connection, workspace_name: str) -> int:
    xml_payload = create_xml_tag("workspace",
                                 create_xml_tag("name", workspace_name))

    response = requests.post(conn.get_url() + "workspaces", xml_payload,
                             headers = {"Content-type": "text/xml"},
                             auth = conn.get_auth())

    return response.status_code

def create_workspace_if_not_found(conn: geoserver_connection, workspace_name: str) -> bool:
    if workspace_name not in get_all_workspace_names(conn):
        status_code = create_workspace(conn, workspace_name)

        return status_code == 201
    return False

class postgis_database_info:
    def __init__(self, name: str, host: str, port: str, user: str, password: str):
        self.name     = name
        self.host     = host
        self.port     = port
        self.user     = user
        self.password = password

    def get_name(self):
        return self.name

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_user(self):
        return self.user

    def get_password(self):
        return self.password

    def get_xml_payload(self) -> str:
        name_tag     = create_xml_tag("name", self.name)
        host_tag     = create_xml_tag("host", self.host)
        port_tag     = create_xml_tag("port", self.port)
        database_tag = create_xml_tag("database", self.name)
        user_tag     = create_xml_tag("user", self.user)
        passwd_tag   = create_xml_tag("passwd", self.password)
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

def get_all_data_store_names_from_workspace(conn: geoserver_connection, workspace_name: str) -> List[str]:
    if workspace_name not in get_all_workspace_names(conn):
        return []

    response = requests.get(conn.get_url() + "workspaces/" + workspace_name + "/datastores",
                            auth = conn.get_auth())

    response_json_dict = json.loads(response.content)
    data_store_data_dict = response_json_dict['dataStores']

    if type(data_store_data_dict) is dict:
        data_store_data_list = data_store_data_dict['dataStore']

        return [ds['name'] for ds in data_store_data_list]
    else:
        return []

def create_database_store_into_workspace(conn: geoserver_connection,
                                         workspace_name: str,
                                         db_info: postgis_database_info) -> int:
    xml_payload = db_info.get_xml_payload()

    response = requests.post(conn.get_url() + "workspaces/" + workspace_name + "/datastores",
                             xml_payload,
                             headers = {"Content-type": "text/xml"},
                             auth = conn.get_auth())

    return response.status_code

def create_database_store_into_workspace_if_not_found(conn: geoserver_connection,
                                                      workspace_name: str,
                                                      db_info: postgis_database_info):
    if workspace_name not in get_all_workspace_names(conn):
        return False
    if db_info.get_name() in get_all_data_store_names_from_workspace(conn, workspace_name):
        return False

    status_code = create_database_store_into_workspace(conn=conn,
                                                       workspace_name=workspace_name,
                                                       db_info=db_info)

    return status_code == 201

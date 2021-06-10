from typing import List
import json

import requests
from requests.auth import HTTPBasicAuth

from .xml import create_xml_tag
from .postgis import postgis_connection

class geoserver_connection:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.url = "http://" + host + ":" + port + "/geoserver/rest/"
        self.auth = HTTPBasicAuth(username, password)


    def get_all_workspace_names(self) -> List[str]:
        response = requests.get(self.url + "workspaces",
                                auth = self.auth)

        response_json_dict = json.loads(response.content)

        workspace_data_list = response_json_dict['workspaces']["workspace"]

        return [ws['name'] for ws in workspace_data_list]


    def create_workspace(self, workspace_name: str) -> int:
        xml_payload = create_xml_tag("workspace",
                                     create_xml_tag("name", workspace_name))

        response = requests.post(self.url + "workspaces", xml_payload,
                                 headers = {"Content-type": "text/xml"},
                                 auth = self.auth)

        return response.status_code

    def create_workspace_if_not_found(self, workspace_name: str) -> bool:
        if workspace_name not in self.get_all_workspace_names():
            status_code = self.create_workspace(workspace_name)

            return status_code == 201
        return False


    def get_all_data_store_names_from_workspace(self, workspace_name: str) -> List[str]:
        if workspace_name not in self.get_all_workspace_names():
            return []

        response = requests.get(self.url +
                                "workspaces/" + workspace_name + "/datastores",
                                auth = self.auth)

        response_json_dict = json.loads(response.content)
        data_store_data_dict = response_json_dict['dataStores']

        if type(data_store_data_dict) is dict:
            data_store_data_list = data_store_data_dict['dataStore']

            return [ds['name'] for ds in data_store_data_list]
        else:
            return []

    def create_database_store_into_workspace(self,
                                             workspace_name: str,
                                             db_conn: postgis_connection) -> int:
        xml_payload = db_conn.get_xml_payload()

        response = requests.post(self.url +
                                 "workspaces/" + workspace_name + "/datastores",
                                 xml_payload,
                                 headers = {"Content-type": "text/xml"},
                                 auth = self.auth)

        return response.status_code

    def create_database_store_into_workspace_if_not_found(self,
                                                          workspace_name: str,
                                                          db_conn: postgis_connection) -> bool:
        if workspace_name not in self.get_all_workspace_names():
            return False
        if db_conn.get_database() in self.get_all_data_store_names_from_workspace(workspace_name):
            return False

        status_code = self.create_database_store_into_workspace(workspace_name=workspace_name,
                                                                db_conn=db_conn)

        return status_code == 201

    def publish_table_from_workspace_database_store(self,
                                                    workspace_name: str,
                                                    db_conn: postgis_connection,
                                                    table_name: str) -> bool:
        xml_payload = create_xml_tag("featureType",
                                     create_xml_tag("name", table_name))

        response = requests.post(self.url +
                                 "workspaces/" + workspace_name +
                                 "/datastores/" + db_conn.get_database() + "/featuretypes",
                                 xml_payload,
                                 headers = {"Content-type": "text/xml"},
                                 auth = self.auth)

        return response.status_code == 201

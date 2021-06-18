from typing import List
import json
import time

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

        self.wait_for_geoserver()

    def wait_for_geoserver(self, time_interval = 10):
        while True:
            response = requests.get(self.url + "workspaces",
                                    auth = self.auth)
            if response.status_code == 200:
                break
            else:
                print("Waiting for GeoServer [%s %s] to be ready" % (self.host, self.port))
                time.sleep(time_interval)

    def get_all_workspace_names(self) -> List[str]:
        response = requests.get(self.url + "workspaces",
                                auth = self.auth)

        response_json_dict = json.loads(response.content)

        workspace_data_list = response_json_dict['workspaces']["workspace"]

        return [ws['name'] for ws in workspace_data_list]


    def create_workspace(self, workspace_name: str) -> int:
        print("Creating workspace %s" % workspace_name)

        xml_payload = create_xml_tag("workspace",
                                     create_xml_tag("name", workspace_name))

        response = requests.post(self.url + "workspaces", xml_payload,
                                 headers = {"Content-type": "text/xml"},
                                 auth = self.auth)

        return response.status_code

    def create_workspace_if_not_found(self, workspace_name: str) -> bool:
        if workspace_name not in self.get_all_workspace_names():
            status_code = self.create_workspace(workspace_name)

            if status_code == 201:
                print("Successfully created workspace %s" % workspace_name)

                return True
            else:
                print("Something went wrong when creating workspace %s" % workspace_name)

                return False
        else:
            print("Workspace %s already exists" % workspace_name)

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
        print("Creating database store %s inside workspace %s" % (db_conn.get_database(), workspace_name))

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
            print("Workspace %s does not exist" % workspace_name)
            
            return False
        if db_conn.get_database() in self.get_all_data_store_names_from_workspace(workspace_name):
            print("Database %s already registered in workspace %s" % (db_conn.get_database(), workspace_name))
            
            return False

        status_code = self.create_database_store_into_workspace(workspace_name=workspace_name,
                                                                db_conn=db_conn)

        if status_code == 201:
            print("Successfully registered database %s into workspace %s" % (db_conn.get_database(), workspace_name))

            return True
        else:
            print("Something went wrong when registering database %s into workspace %s" % (db_conn.get_database(), workspace_name))

            return False

    def get_table_names_from_database_store_in_workspace(self,
                                                         workspace_name: str,
                                                         db_conn: postgis_connection) -> List[str]:
        if workspace_name not in self.get_all_workspace_names():
            return []
        if db_conn.get_database() not in self.get_all_data_store_names_from_workspace(workspace_name):
            return []

        response = requests.get(self.url +
                                "workspaces/" + workspace_name +
                                "/datastores/" + db_conn.get_database() + "/featuretypes.json",
                                auth = self.auth)

        response_json_dict = json.loads(response.content)
        featuretypes_data_dict = response_json_dict["featureTypes"]

        if type(featuretypes_data_dict) is dict:
            featuretypes_data_list = featuretypes_data_dict["featureType"]

            return [ft["name"] for ft in featuretypes_data_list]
        else:
            return []


    def publish_table_from_workspace_database_store(self,
                                                    workspace_name: str,
                                                    db_conn: postgis_connection,
                                                    table_name: str) -> bool:
        print("Publishing table %s from database %s into workspace %s" % (table_name, db_conn.get_database(), workspace_name))

        xml_payload = create_xml_tag("featureType",
                                     create_xml_tag("name", table_name))

        response = requests.post(self.url +
                                 "workspaces/" + workspace_name +
                                 "/datastores/" + db_conn.get_database() + "/featuretypes",
                                 xml_payload,
                                 headers = {"Content-type": "text/xml"},
                                 auth = self.auth)

        return response.status_code


    def publish_table_from_workspace_database_store_if_not_found(self,
                                                                 workspace_name: str,
                                                                 db_conn: postgis_connection,
                                                                 table_name: str) -> bool:
        if workspace_name not in self.get_all_workspace_names():
            print("Workspace %s does not exist" % workspace_name)

            return False
        if db_conn.get_database() not in self.get_all_data_store_names_from_workspace(workspace_name):
            print("Database %s does not exist in workspace %s" % (db_conn.get_database(), workspace_name))

            return False
        if table_name in self.get_table_names_from_database_store_in_workspace(workspace_name, db_conn):
            print("Table %s already published in workspace %s from database %s" % (table_name, workspace_name, db_conn.get_database()))

            return False

        status_code = self.publish_table_from_workspace_database_store(workspace_name, db_conn, table_name)

        if status_code == 201:
            print("Successfully published table %s from database %s in workspace %s" % (table_name, db_conn.get_database(), workspace_name))

            return True
        else:
            print("Something went wrong when publishing table %s from database %s in workspace %s" % (table_name, db_conn.get_database(), workspace_name))

            return False

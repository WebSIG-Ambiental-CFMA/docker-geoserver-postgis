from typing import List
from .geoserver import geoserver_connection
from .postgis import postgis_connection

class init_manager:
    def __self__(self,
                 geo_conn: geoserver_connection,
                 pgs_conn: postgis_connection,
                 workspace_name: str,
                 scripts_dir: str):
        self.geo_conn = geo_conn
        self.pgs_conn = pgs_conn
        self.workspace_name = workspace_name
        self.scripts_dir = scripts_dir

    def initialize(self):
        self.geo_conn.create_workspace_if_not_found(self.workspace_name)
        self.geo_conn.create_database_store_into_workspace_if_not_found(self.workspace_name, self.pgs_conn)

    def register_table(self, sql_script: str):
        import os

        base_table_name, _ = os.path.splitext(sql_script)

        full_table_name = self.scripts_dir + "/" + base_table_name

        self.pgs_conn.execute_sql_script(sql_script)
        self.geo_conn.publish_table_from_workspace_database_store(self.workspace_name,
                                                                  self.pgs_conn,
                                                                  full_table_name)

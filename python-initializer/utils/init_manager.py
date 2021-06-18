from typing import List
from .geoserver import geoserver_connection
from .postgis import postgis_connection

class init_manager:
    def __init__(self,
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

        full_filename = self.scripts_dir + "/" + sql_script

        self.pgs_conn.execute_sql_script(full_filename)
        self.geo_conn.publish_table_from_workspace_database_store_if_not_found(self.workspace_name,
                                                                               self.pgs_conn,
                                                                               base_table_name)

    def register_tables(self, sql_scripts: List[str]):
        for sql_script in sql_scripts:
            self.register_table(sql_script)

    def register_tables_from_scripts_dir(self):
        from os import listdir
        from os.path import isfile, join

        scripts_dir_filenames = [f for f in listdir(self.scripts_dir) if isfile(join(self.scripts_dir, f))]

        sql_scripts = filter(lambda f: f.endswith(".sql"), scripts_dir_filenames)

        self.register_tables(sql_scripts)

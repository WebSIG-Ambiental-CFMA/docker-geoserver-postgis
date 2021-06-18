import time

import psycopg2

from .xml import create_xml_tag

class postgis_connection:
    def __init__(self, host: str, port: str, database: str, user: str, password: str):
        self.host     = host
        self.port     = port
        self.database = database
        self.user     = user
        self.password = password

        self.wait_for_database()

        self.conn = psycopg2.connect(host=self.host,
                                     port=self.port,
                                     database=self.database,
                                     user=self.user,
                                     password=self.password)

    def wait_for_database(self, time_interval = 10):
        while True:
            try:
                temp_conn = psycopg2.connect(host=self.host,
                                             port=self.port,
                                             database=self.database,
                                             user=self.user,
                                             password=self.password)
                temp_conn.close()
                break
            except:
                print("Waiting [%s %s %s %s] to be ready" % (self.host,
                                                             self.port,
                                                             self.database,
                                                             self.user))
                time.sleep(time_interval)

    def get_database(self):
        return self.database

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_user(self):
        return self.user

    def get_password(self):
        return self.password

    def get_xml_payload(self) -> str:
        name_tag     = create_xml_tag("name", self.database)
        host_tag     = create_xml_tag("host", self.host)
        port_tag     = create_xml_tag("port", self.port)
        database_tag = create_xml_tag("database", self.database)
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

    def execute_statement(self, sql_statement: str):
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_statement)
            print("Successfully executed SQL script:\n%s" % sql_statement)
        except:
            print("Something went wrong when executing SQL statement:\n %s" % sql_statement)
            self.conn.rollback()
            print("Peformed rollback in database")

            return []

        result = None
        try:
            result = cursor.fetchall()
        except:
            result = []

        self.conn.commit()

        cursor.close()

        return result

    def execute_sql_script(self, sql_filename: str):
        print("Executing SQL script %s" % sql_filename)

        file = open(sql_filename, "r")

        file_content = file.read()

        file.close()

        return self.execute_statement(file_content)

    def close(self):
        self.conn.close()

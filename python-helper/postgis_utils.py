import psycopg2

class postgis_connection:
    def __init__(self, host: str, port: str, database: str, user: str, password: str):
        self.host     = host
        self.port     = port
        self.database = database
        self.user     = user
        self.password = password

        self.conn = psycopg2.connect(host=self.host,
                                     port=self.port,
                                     database=self.database,
                                     user=self.user,
                                     password=self.password)

    def execute_statement(self, sql_statement: str):
        cursor = self.conn.cursor()

        try:
            cursor.execute(sql_statement)
        except:
            self.conn.rollback()

            return []

        result = None
        try:
            result = cursor.fetchall()
        except:
            result = []

        cursor.close()

        return result

    def execute_sql_script(self, sql_filename: str):
        file = open(sql_filename, "r")

        file_content = file.read()

        file.close()

        return self.execute_statement(file_content)

    def close(self):
        self.conn.close()

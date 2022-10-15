import mysql.connector


class MySqlDBManager:
    def __init__(self, username, password, host, db, port):
        self.username = username
        self.password = password
        self.host = host
        self.db = db
        self.port = port
        self.connection = mysql.connector.connect(user=self.username,
                                                  password=self.password,
                                                  host=self.host,
                                                  database=self.db,
                                                  auth_plugin='mysql_native_password',
                                                  port=int(port))
        self.cur=self.connection.cursor(buffered=True)

    def excute_query(self, query):
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(query)
            self.connection.commit()
            cursor.close()
        except:
            self.connection = mysql.connector.connect(user=self.username,
                                                      password=self.password,
                                                      host=self.host,
                                                      database=self.db,
                                                      auth_plugin='mysql_native_password')
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
            cursor.close()

    def excute_query_fetchall(self, query):
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            return records
        except:
            self.connection = mysql.connector.connect(user=self.username,
                                                      password=self.password,
                                                      host=self.host,
                                                      database=self.db,
                                                      auth_plugin='mysql_native_password')
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(query)
            records = cursor.fetchall()
            cursor.close()
            return records


    def excute_query_fetchone(self, query):
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.reset()
            cursor.execute(query)
            record = cursor.fetchone()
            cursor.close()
            return record
        except:
            self.connection = mysql.connector.connect(user=self.username,
                                                      password=self.password,
                                                      host=self.host,
                                                      database=self.db,
                                                      auth_plugin='mysql_native_password')
            cursor = self.connection.cursor(buffered=True)
            cursor.execute(query)
            record = cursor.fetchone()
            cursor.close()
            return record

    def execute_many_query(self, query, records):
        try:
            cursor = self.connection.cursor(buffered=True)
            cursor.executemany(query, records)
            self.connection.commit()
            cursor.close()
            return records
        except:
            self.connection = mysql.connector.connect(user=self.username,
                                                      password=self.password,
                                                      host=self.host,
                                                      database=self.db,
                                                      auth_plugin='mysql_native_password')
            cursor = self.connection.cursor(buffered=True)
            cursor.executemany(query, records)
            self.connection.commit()
            cursor.close()
            return records

    def close_connection(self):
        self.connection.close()
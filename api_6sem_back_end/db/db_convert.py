import os
from db_configuration import db_connection_mongo, db_connection_sql_server

def convert_db_sql_server_to_mongodb(db_name_sql, db_name_mongo):
    sql_conn = db_connection_sql_server(
        os.getenv("DB_DRIVER"),
        os.getenv("DB_SERVER"),
        os.getenv("DB_DATABASE")
    )
    mongo_client = db_connection_mongo(os.getenv("MONGO_URI"))

    if not sql_conn or not mongo_client:
        print("Erro: não foi possível conectar ao banco de dados.")
        return

    cursor = sql_conn.cursor()
    cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
    tables = cursor.fetchall()

    print(tables)

if __name__ == '__main__':
    convert_db_sql_server_to_mongodb('test', 'test')
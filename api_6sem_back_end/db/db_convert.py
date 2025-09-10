import os
from db_configuration import db_connection_mongo, db_connection_sql_server
import datetime

def convert_db_sql_server_to_mongodb():
    data_tables = {}
    sql_conn = db_connection_sql_server(
        os.getenv("DB_DRIVER"),
        os.getenv("DB_SERVER"),
        os.getenv("DB_DATABASE")
    )

    mongo_client = db_connection_mongo(os.getenv("DB_URL_MONGO"))

    if not sql_conn or not mongo_client:
        print("Erro: não foi possível conectar ao banco de dados.")
        return

    cursor = sql_conn.cursor()
    name_tables = cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")

    for i in name_tables:
        table_name = i[0]
        data_tables = cursor.execute(f"SELECT * FROM {table_name}")

        columns = [table_name[0] for table_name in cursor.description]
        rows = data_tables.fetchall()
        print(rows)

        bson = [
            {col: (datetime.datetime(val.year, val.month, val.day) if isinstance(val, datetime.date) and not isinstance(
                val, datetime.datetime) else val)
             for col, val in zip(columns, row)}
            for row in rows
        ]

        db = mongo_client["api6bd"]
        collection = db[table_name]

        if bson:
            collection.insert_many(bson)
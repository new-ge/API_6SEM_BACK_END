import os
from db_configuration import db_connection_mongo, db_connection_sql_server
import datetime
from db_security import encrypt_data

def process_data_sql_server():
    sql_conn = db_connection_sql_server(
        os.getenv("DB_DRIVER"),
        os.getenv("DB_SERVER"),
        os.getenv("DB_DATABASE")
    )

    cursor = sql_conn.cursor()
    name_tables = cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")

    for i in name_tables:
        table_name = i[0]
        data_tables = cursor.execute(f"SELECT * FROM {table_name}")

        columns = [table_name[0] for table_name in cursor.description]
        rows = data_tables.fetchall()

        bson = [
            {col: (datetime.datetime(val.year, val.month, val.day) if isinstance(val, datetime.date) and not isinstance(
                val, datetime.datetime) else val)
            for col, val in zip(columns, row)}
            for row in rows
        ]

    return bson

def save_on_mongo_db(bson_encrypted, table_name):
    mongo_client = db_connection_mongo(
        os.getenv("DB_URL_MONGO")
    )
    db = mongo_client[os.getenv("DB_MONGO")]
    name_collection = db[table_name]

    if bson_encrypted:
        name_collection.insert_many(bson_encrypted)
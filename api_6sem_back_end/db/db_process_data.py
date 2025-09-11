import os
from ..db.db_configuration import db_connection_mongo, db_connection_sql_server
import datetime
from ..db.db_security import encrypt_data
from ..config.keep_columns import columns_to_keep
from ..config.sensitive_fields import sensitive_fields
from concurrent.futures import ThreadPoolExecutor

def process_data_sql_server():
    sql_conn = db_connection_sql_server(
        os.getenv("DB_DRIVER"),
        os.getenv("DB_SERVER"),
        os.getenv("DB_DATABASE")
    )

    cursor = sql_conn.cursor()
    name_tables = cursor.execute(f"SELECT DISTINCT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'").fetchall()

    all_tables = {}
    columns_by_table = {}

    for i in name_tables:
        table_name = i[0]

        if table_name in columns_to_keep:
            cols = ", ".join(columns_to_keep[table_name])
            query = f"SELECT {cols} FROM {table_name}"

            data_tables = cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            rows = data_tables.fetchall()

            bson = [
                {
                    col: (
                        datetime.datetime(val.year, val.month, val.day)
                        if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime)
                        else val
                    )
                    for col, val in zip(columns, row)
                }
                for row in rows
            ]

            all_tables[table_name] = bson
            columns_by_table[table_name] = columns  
        else:
            pass

    return all_tables, name_tables, columns

def handle_data_bson(all_tables):
    
    status_lookup = {row["StatusId"]: row["Name"] for row in all_tables["Statuses"]}

    for row in all_tables["TicketStatusHistory"]:
        from_id = row.pop("FromStatusId", None)
        to_id = row.pop("ToStatusId", None)
        
        row["FromStatusName"] = status_lookup.get(from_id)
        row["ToStatusName"] = status_lookup.get(to_id)

    return all_tables

def encrypt_sensitive_fields_bson(all_tables):
    for table_name, rows in all_tables.items():
        fields_to_encrypt = sensitive_fields.get(table_name)
        if not fields_to_encrypt:
            continue

        fields_to_encrypt = set(fields_to_encrypt)

        def encrypt_row(row):
            for field in fields_to_encrypt & row.keys():
                row[field] = encrypt_data(row[field])
            return row

        all_tables[table_name] = list(map(encrypt_row, rows))

    return all_tables

def create_collections_mongo_db(all_tables):
    department_lookup = {d["DepartmentId"]: d["Name"] for d in all_tables["Departments"]}

    users_docs = []
    for agent in all_tables["Agents"]:
        doc = {
            "name": agent["FullName"],
            "email": agent["Email"],
            "department": department_lookup.get(agent.get("DepartmentId")),
            "role": "",
            "isActive": agent.get("IsActive", True),
            "login": {
                "username": "",
                "password": ""
            }
        }
    users_docs.append(doc)


def save_on_mongo_db(bson_encrypted, table_name, docs):
    mongo_client = db_connection_mongo(
        os.getenv("DB_URL_MONGO")
    )

    db = mongo_client[os.getenv("DB_MONGO")]
    name_collection = db[table_name]

    if bson_encrypted:
        name_collection.insert_many(docs)
import os
from api_6sem_back_end.db.db_configuration import db_connection_mongo, db_connection_sql_server
import datetime
from api_6sem_back_end.db.db_security import encrypt_data
from pymongo.errors import BulkWriteError, DuplicateKeyError
import json
from bson import ObjectId

users_docs = []
tickets_docs = []
history_docs = []

def process_data_sql_server(columns_to_keep):
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

    return all_tables, name_tables

def encrypt_sensitive_fields_bson(all_tables, sensitive_fields):
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
    status_lookup = {d["StatusId"]: d["Name"] for d in all_tables["Statuses"]}
    priority_lookup = {d["PriorityId"]: d["Name"] for d in all_tables["Priorities"]}
    sla_plains_lookup = {
        d["SLAPlanId"]: {"name": d["Name"], "target_minutes": d["ResolutionMins"]}
        for d in all_tables["SLA_Plans"]
    }
    product_lookup = {d["ProductId"]: d["Name"] for d in all_tables["Products"]}
    category_lookup = {d["CategoryId"]: d["Name"] for d in all_tables["Categories"]}
    sub_category_lookup = {d["SubcategoryId"]: d["Name"] for d in all_tables["Subcategories"]}

    history_by_ticket = {}

    for h in all_tables["TicketStatusHistory"]:
        if h.get("TicketId") not in history_by_ticket:
            history_by_ticket[h.get("TicketId")] = []
        history_by_ticket[h.get("TicketId")].append({
            "from": status_lookup.get(h.get("FromStatusId")),
            "to": status_lookup.get(h.get("ToStatusId")),
        })

    for agent in all_tables["Agents"]:
        user_collection = {
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
        users_docs.append(user_collection)

    for ticket in all_tables["Tickets"]:
        ticket_collection = {
            "title": ticket["Title"],
            "description": ticket["Description"],
            "status": status_lookup.get(ticket.get("StatusId") or ticket.get("CurrentStatusId")),
            "priority": priority_lookup.get(ticket.get("PriorityId")),
            "sla": {
                "name": sla_plains_lookup.get(ticket.get("SLAPlanId"), {}).get("name"),
                "target_minutes": sla_plains_lookup.get(ticket.get("SLAPlanId"), {}).get("target_minutes"),
            },
            "product": product_lookup.get(ticket.get("ProductId")),
            "category": category_lookup.get(ticket.get("CategoryId")),
            "sub_category": sub_category_lookup.get(ticket.get("SubcategoryId")),
            "history": history_by_ticket.get(ticket["TicketId"], [])
        }
        tickets_docs.append(ticket_collection)

    for history in all_tables["AuditLogs"]:
        history_collection = {
            "name": history["PerformedBy"],
            "operation": history["Operation"],
            "performed_at": history["PerformedAt"],
            "changed_field": list(json.loads(history["DetailsJson"]).values())[0]
        }
        history_docs.append(history_collection)

    return history_docs, tickets_docs, users_docs

def save_on_mongo_db(**collections_docs):
    mongo_client = db_connection_mongo(
        os.getenv("DB_URL_MONGO")
    )
    db = mongo_client[os.getenv("DB_MONGO")]

    for collection_name, docs in collections_docs.items():
        if not docs:
            continue

        for doc in docs:
            if "_id" not in doc:
                if doc.get("id") or doc.get("TicketId"):
                    doc["_id"] = ObjectId(str(doc.get("id") or doc.get("TicketId")))
                else:
                    doc["_id"] = ObjectId()
            try:
                db[collection_name].update_one(
                    {"_id": doc["_id"]},
                    {"$set": doc},
                    upsert=True
                )
            except (DuplicateKeyError, BulkWriteError):
                pass
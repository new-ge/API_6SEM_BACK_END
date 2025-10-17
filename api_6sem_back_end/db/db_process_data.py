import os
from api_6sem_back_end.db.db_configuration import db_connection_sql_server, db_data
import datetime
from flair.models import TextClassifier
from flair.data import Sentence
from pymongo.errors import BulkWriteError
from pymongo import UpdateOne
import json

_model = None

def get_sentiment_model():
    global _model
    if _model is None:
        print("Carregando modelo de sentimento do Flair...")
        _model = TextClassifier.load('sentiment-fast')
    return _model

def predict_sentiment(text: str) -> str:
    model = get_sentiment_model()
    sentence = Sentence(text)
    model.predict(sentence)
    label = sentence.labels[0]
    return label.value

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
    tag_lookup = {t["TagId"]: t["Name"] for t in all_tables["Tags"]}
    access_level_lookup = {t["NivelId"]: t["Acesso"] for t in all_tables["AccessLevel"]}
    agent_access_lookup = {
        agent["AgentId"]: access_level_lookup.get(agent.get("NivelId"))
        for agent in all_tables["Agents"]
    }

    tags_by_ticket = {}
    for tt in all_tables["TicketTags"]:
        ticket_id = tt.get("TicketId")
        tag_id = tt.get("TagId")
        if ticket_id not in tags_by_ticket:
            tags_by_ticket[ticket_id] = []
        tags_by_ticket[ticket_id].append(tag_lookup.get(tag_id))

    history_by_ticket = {}
    for h in all_tables["TicketStatusHistory"]:
        if h.get("TicketId") not in history_by_ticket:
            history_by_ticket[h.get("TicketId")] = []
        history_by_ticket[h.get("TicketId")].append({
            "from": status_lookup.get(h.get("FromStatusId")),
            "to": status_lookup.get(h.get("ToStatusId")),
        })

    users_docs, tickets_docs, history_docs = [], [], []

    for agent in all_tables["Agents"]:
        user_collection = {
            "agent_id": agent["AgentId"],
            "name": agent["FullName"],
            "email": agent["Email"],
            "department": department_lookup.get(agent.get("DepartmentId")),
            "role": access_level_lookup.get(agent.get("NivelId")).strip(),
            "isActive": agent.get("IsActive", True),
            "login": {
                "username": "",
                "password": ""
            }
        }
        users_docs.append(user_collection)

    for ticket in all_tables["Tickets"]:

        sentiment = predict_sentiment(ticket["Description"]) if ticket["Description"] else None

        ticket_collection = {
            "ticket_id": ticket["TicketId"],
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
            "tag": tags_by_ticket.get(ticket["TicketId"], []),
            "history": history_by_ticket.get(ticket["TicketId"], []),
            "created_at": ticket["CreatedAt"],
            "closed_at": ticket["ClosedAt"],
            "access_level": agent_access_lookup.get(ticket.get("AssignedAgentId")).strip(),
            "sentiment": sentiment
        }
        tickets_docs.append(ticket_collection)

    for history in all_tables["AuditLogs"]:
        history_collection = {
            "audit_id": history["AuditId"],
            "name": history["PerformedBy"],
            "operation": history["Operation"],
            "performed_at": history["PerformedAt"],
            "changed_field": list(json.loads(history["DetailsJson"]).values())[0]
        }
        history_docs.append(history_collection)

    return history_docs, tickets_docs, users_docs

def save_on_mongo_db_collections(**collections_docs):
    for collection_name in collections_docs.keys():
        db_data[collection_name].create_index("agent_id", unique=True, sparse=True)
        db_data[collection_name].create_index("audit_id", unique=True, sparse=True)
        db_data[collection_name].create_index("ticket_id", unique=True, sparse=True)

    for collection_name, docs in collections_docs.items():
        if not docs:
            continue

        operations = []
        for doc in docs:
            if doc.get("agent_id"):
                filter_query = {"agent_id": doc["agent_id"]}
            elif doc.get("audit_id"):
                filter_query = {"audit_id": doc["audit_id"]}
            elif doc.get("ticket_id"):
                filter_query = {"ticket_id": doc["ticket_id"]}
            else:
                continue

            operations.append(
                UpdateOne(
                    filter_query,
                    {"$set": doc},
                    upsert=True
                )
            )

        if operations:
            try:
                result = db_data[collection_name].bulk_write(operations, ordered=False)

                print(
                    f"[{collection_name}] "
                    f"Inseridos: {result.upserted_count}, "
                    f"Atualizados: {result.modified_count}, "
                    f"Ignorados: {len(operations) - result.upserted_count - result.modified_count}"
                )
            except BulkWriteError as e:
                print(f"Erro ao salvar: {e.details}")
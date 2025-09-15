from fastapi import FastAPI
from api_6sem_back_end.routers import router_opened, router_average_time, router_by_period
from api_6sem_back_end.db.db_configuration import db_connection_mongo
from api_6sem_back_end.db.db_process_data import process_data_sql_server, encrypt_sensitive_fields_bson, create_collections_mongo_db, save_on_mongo_db
from api_6sem_back_end.config.keep_columns import columns_to_keep
from api_6sem_back_end.config.sensitive_fields import sensitive_fields

import os
from dotenv import load_dotenv
import glob
import datetime

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "*.env"))
load_dotenv(dotenv_path[0])
app = FastAPI()

app.include_router(router_opened.router)
app.include_router(router_average_time.router)
app.include_router(router_by_period.router)

db = db_connection_mongo(os.getenv("DB_URL_MONGO"))[os.getenv("DB_MONGO")]
collection = db["tickets"]

@app.get("/")
async def root():
    all_tables = process_data_sql_server(columns_to_keep)
    all_tables = encrypt_sensitive_fields_bson(all_tables, sensitive_fields)
    history_docs, tickets_docs, users_docs = create_collections_mongo_db(all_tables)
    save_on_mongo_db(
        history = history_docs,
        tickets = tickets_docs,
        users = users_docs
    )


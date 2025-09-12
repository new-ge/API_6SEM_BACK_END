from fastapi import FastAPI
from api_6sem_back_end.db.db_process_data import encrypt_sensitive_fields_bson, create_collections_mongo_db, process_data_sql_server, save_on_mongo_db
from api_6sem_back_end.config.keep_columns import columns_to_keep
from api_6sem_back_end.config.sensitive_fields import sensitive_fields
import os
from dotenv import load_dotenv
import glob

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "*.env"))
load_dotenv(dotenv_path[0])

app = FastAPI()

@app.get("/")
async def root():
    all_tables, name_tables = process_data_sql_server(columns_to_keep)
    all_tables = encrypt_sensitive_fields_bson(all_tables, sensitive_fields)
    history_docs, tickets_docs, users_docs = create_collections_mongo_db(all_tables)
    return save_on_mongo_db(
        history=history_docs,
        tickets=tickets_docs,
        users=users_docs
    )
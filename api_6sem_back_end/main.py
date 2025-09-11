from fastapi import FastAPI
from api_6sem_back_end.db.db_process_data import encrypt_sensitive_fields_bson, create_tables_mongo_db, process_data_sql_server
from api_6sem_back_end.config.sensitive_fields import sensitive_fields

app = FastAPI()


@app.get("/")
async def root():
    a, b, c = process_data_sql_server()
    return create_tables_mongo_db(a)
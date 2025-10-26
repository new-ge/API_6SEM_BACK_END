import pyodbc
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import glob

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "..", "*.env"))
load_dotenv(dotenv_path[0])

def db_connection_sql_server(url_driver: str, server: str, db_name: str):
    conn_str = (
        f"DRIVER={{{url_driver}}};"
        f"SERVER={server};"
        f"DATABASE={db_name};"
        f"Trusted_Connection=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        print("Conexão bem-sucedida!")
        return conn
    except Exception as e:
        print("Erro na conexão:", e)
        return None

def db_connection_mongo(url_mongo: str, db_name: str):
    uri = url_mongo

    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=9999999,
            connectTimeoutMS=None,
            socketTimeoutMS=None,
            tls=True
        )
        print(f"Conexão bem-sucedida!")
        return client[db_name]
    except Exception as e:
        print("Erro na conexão:", e)
        return None
    
db_data = db_connection_mongo(os.getenv("DB_URL_MONGO"), os.getenv("DB_MONGO"))
db_deleted = db_connection_mongo(os.getenv("DB_URL_MONGO"), os.getenv("DB_MONGO_2"))


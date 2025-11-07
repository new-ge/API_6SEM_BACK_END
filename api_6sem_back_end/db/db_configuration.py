import pyodbc
from pymongo import MongoClient, errors
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

class MongoConnection:
    _client = None

    @staticmethod
    def get_client():
        if MongoConnection._client is None:
            try:
                uri = os.getenv("DB_URL_MONGO")
                MongoConnection._client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=9999999,
                    connectTimeoutMS=None,
                    socketTimeoutMS=None,
                    tls=True
                )
                MongoConnection._client.admin.command("ping")
                print("Conexão MongoDB bem-sucedida!")
            except errors.ConnectionFailure as e:
                print("Erro ao conectar ao MongoDB:", e)
                MongoConnection._client = None
        return MongoConnection._client

    @staticmethod
    def get_db(db_name: str):
        client = MongoConnection.get_client()
        return client[db_name] if client else None

    @staticmethod
    def close():
        if MongoConnection._client:
            MongoConnection._client.close()
            MongoConnection._client = None
            print("Conexão MongoDB encerrada.")

db_principal = MongoConnection.get_db(os.getenv("DB_MONGO"))
db_deleted = MongoConnection.get_db(os.getenv("DB_MONGO_2"))
db_backup = MongoConnection.get_db(os.getenv("DB_MONGO_BACKUPS"))
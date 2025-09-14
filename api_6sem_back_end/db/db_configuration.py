import pyodbc
from pymongo import MongoClient

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

def db_connection_mongo(url_mongo: str):
    uri = url_mongo

    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=999999999,
            connectTimeoutMS=None,
            socketTimeoutMS=None,
            tls=True
        )
        print("Conexão bem-sucedida!")
        return client
    except Exception as e:
        print("Erro na conexão:", e)
        return None
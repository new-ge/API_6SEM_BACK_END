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

def db_connection_mongo(url_mongo: str):
    uri = url_mongo
    try:
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=99999999,
            connectTimeoutMS=None,
            socketTimeoutMS=None,
            tls=True
        )
        print("Conexão bem-sucedida!")
        db = client[os.getenv("DB_MONGO")]
        return db
    except Exception as e:
        print("Erro na conexão:", e)
        return None

# Realiza a conexão MongoDB
db = db_connection_mongo(os.getenv("DB_URL_MONGO"))

# Exemplo de verificação da coleção
if db is not None:  # Compare explicitamente com None
    try:
        # Suponha que você tenha uma coleção chamada 'tickets'
        tickets_collection = db["tickets"]
        # Listar alguns documentos da coleção
        for ticket in tickets_collection.find().limit(5):
            print(ticket)
    except Exception as e:
        print("Erro ao acessar a coleção:", e)
else:
    print("Erro: Não foi possível conectar ao banco de dados MongoDB.")

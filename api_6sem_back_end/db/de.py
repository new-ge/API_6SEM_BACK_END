import pyodbc
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Carrega o .env da raiz do projeto
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "a.env"))

# -----------------------------
# Conexão com SQL Server
# -----------------------------
def db_connection_sql_server(url_driver: str, server: str, db_name: str):
    conn_str = (
        f"DRIVER={{{url_driver}}};"
        f"SERVER={server};"
        f"DATABASE={db_name};"
        f"Trusted_Connection=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        print("✅ Conexão SQL Server bem-sucedida!")
        return conn
    except Exception as e:
        print("❌ Erro na conexão SQL Server:", e)
        return None

# -----------------------------
# Conexão com MongoDB
# -----------------------------
def db_connection_mongo(url_mongo: str, db_name: str):
    if not url_mongo or not db_name:
        raise RuntimeError("❌ DB_URL_MONGO ou DB_MONGO não definidos no .env")
    try:
        client = MongoClient(
            url_mongo,
            serverSelectionTimeoutMS=10000,
            tls=True
        )
        print("✅ Conexão MongoDB bem-sucedida!")
        return client[db_name]
    except Exception as e:
        print("❌ Erro na conexão MongoDB:", e)
        return None

# -----------------------------
# Instâncias globais
# -----------------------------
DB_URL_MONGO = os.getenv("DB_URL_MONGO")
DB_MONGO = os.getenv("DB_MONGO", "bd6sem-luminia")  # fallback se não achar no .env

db_data = db_connection_mongo(DB_URL_MONGO, DB_MONGO)

# Se quiser validar logo na inicialização:
if db_data is None:
    raise RuntimeError("❌ Não foi possível inicializar a conexão com o MongoDB")

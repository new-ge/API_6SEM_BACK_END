import pyodbc
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import glob
import certifi


# 🔧 Localiza e carrega automaticamente o arquivo .env (ex: C:\PROJETOS PYTHON\API_6SEM_BACK_END\a.env)
dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "..", "*.env"))
if dotenv_path:
    load_dotenv(dotenv_path[0])
    print(f"✅ Arquivo .env carregado: {dotenv_path[0]}")
else:
    print("⚠️ Nenhum arquivo .env encontrado!")


# 🔗 Função para conexão com SQL Server (mantida para compatibilidade)
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
        print("❌ Erro na conexão SQL:", e)
        return None


# 🍃 Função para conexão com o MongoDB Atlas
def db_connection_mongo(url_mongo: str, db_name: str):
    try:
        if not url_mongo or not db_name:
            raise ValueError("URL do MongoDB ou nome do banco está ausente (.env não carregado corretamente).")

        client = MongoClient(
            url_mongo,
            tls=True,
            tlsAllowInvalidCertificates=False,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=20000
        )

        # Força teste de conexão
        client.server_info()

        db = client[db_name]
        print(f"✅ Conexão MongoDB bem-sucedida → Banco ativo: {db.name}")
        return db

    except Exception as e:
        print("❌ Erro na conexão MongoDB:", e)
        return None


# 🚀 Inicializa as conexões com os bancos
db_data = db_connection_mongo(os.getenv("DB_URL_MONGO"), os.getenv("DB_MONGO"))  # Banco principal
db_deleted = db_connection_mongo(os.getenv("DB_URL_MONGO"), os.getenv("DB_MONGO_2"))  # Banco de usuários deletados

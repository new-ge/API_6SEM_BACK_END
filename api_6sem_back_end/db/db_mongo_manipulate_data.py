from datetime import datetime, time, timedelta, timezone
import glob
import os
from dotenv import load_dotenv
from pymongo import errors
from api_6sem_back_end.db.db_configuration import MongoConnection

dotenv_path = glob.glob(os.path.join(os.path.dirname(__file__), "*.env"))
load_dotenv(dotenv_path[0])

target_db_name = os.getenv("DB_MONGO_BACKUPS")
db_principal_name = os.getenv("DB_MONGO")

db_principal = MongoConnection.get_db(os.getenv("DB_MONGO"))
db_deleted = MongoConnection.get_db(os.getenv("DB_MONGO_2"))
db_backup = MongoConnection.get_db(target_db_name)

def delete_user(id_user: int):
    delete_user_doc = {
        "agent_id": id_user,
        "timestamp": datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')
    }

    db_deleted["deleted-users"].insert_one(delete_user_doc)

    db_principal["users"].delete_one(
        {"agent_id": id_user}
    )

def ao_detectar_banco() -> bool:
    ids_deleted = [d["agent_id"] for d in db_backup["backups"].find()]
    base_principal = [d["agent_id"] for d in db_deleted["deleted-users"].find()]
    db_rest = list(set(ids_deleted) - set(base_principal))

    docs_para_inserir = list(db_backup["backups"].find({"agent_id": {"$in": db_rest}}))

    if not docs_para_inserir:
        print("Nenhum documento novo para inserir.")
        return False

    try:
        db_principal["users"].insert_many(docs_para_inserir, ordered=False)
        print(f"Inseridos {len(docs_para_inserir)} documentos na base principal.")
    except errors.BulkWriteError as e:
        duplicated = [err for err in e.details["writeErrors"] if err["code"] == 11000]
        inserted = len(docs_para_inserir) - len(duplicated)
        print(f"Ignorados {len(duplicated)} duplicados. Inseridos {inserted} novos.")
    return True

import time
from pymongo import errors

def monitorar_backup():
    backups_existentes = list(db_backup["backups"].find())
    
    if backups_existentes:
        print(f"Detectados {len(backups_existentes)} backups existentes. Processando...")
        inserted = ao_detectar_banco()
        if inserted:
            MongoConnection.get_client().drop_database(target_db_name)
            print(f"Database '{target_db_name}' apagado após processar backups existentes.\n")
    print(f"Monitorando '{target_db_name}.backups' continuamente em tempo real...")

    while True:
        try:
            with db_backup["backups"].watch(full_document="updateLookup") as stream:
                for change in stream:
                    if change.get("operationType") == "insert":
                        print("\nNovo backup detectado. Processando...")

                        inserted = ao_detectar_banco()
                        if inserted:
                            MongoConnection.get_client().drop_database(target_db_name)
                            print(f"Database '{target_db_name}' apagado após processar.")

                        print("Reiniciando monitoramento em 3 segundos...\n")
                        time.sleep(3)
                        break 

        except errors.PyMongoError as e:
            print(f"Erro no Change Stream: {e}")
            print("Tentando novamente em 5 segundos...\n")
            time.sleep(5)
        except KeyboardInterrupt:
            print("Monitoramento interrompido manualmente.")
            break
        except Exception as e:
            print(f"Erro inesperado: {e}")
            time.sleep(5)
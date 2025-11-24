from datetime import datetime, time, timedelta, timezone
import threading
from pymongo import errors
from api_6sem_back_end.db.db_configuration import db_data, db_deleted, db_backup

collection_deleted_users = db_deleted["deleted-users"]
collection_users = db_data["users"]

def find_users_by_ids(ids: list[int]):
    return list(collection_users.find(
        {"agent_id": {"$in": ids}},
        {"_id": 0, "name": 1, "agent_id": 1}
    ))

def delete_users(agent_ids: list[int]):
    timestamp = datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')

    deleted_docs = []
    for agent_id in agent_ids:
        deleted_docs.append({
            "agent_id": agent_id,
            "timestamp": timestamp
        })

    collection_deleted_users.insert_many(deleted_docs)

    collection_users.update_many(
        {"agent_id": {"$in": agent_ids}},
        {
            "$set": {
                "department": None,
                "email": None,
                "login": None,
                "name": None,
                "role": None,
                "isActive": False,
                "modified_at": timestamp
            }
        }
    )

def ao_detectar_banco() -> bool:
    ids_deleted = [d["agent_id"] for d in db_backup["backups"].find()]
    base_principal = [d["agent_id"] for d in db_deleted["deleted-users"].find()]
    db_rest = list(set(ids_deleted) - set(base_principal))

    docs_para_inserir = list(db_backup["backups"].find({"agent_id": {"$in": db_rest}}))

    if not docs_para_inserir:
        return False

    try:
        db_data["users"].insert_many(docs_para_inserir, ordered=False)
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
            db_backup.client.drop_database("backups-luminia")
            print(f"Database apagado após processar backups existentes.\n")
    print(f"Monitorando continuamente em tempo real...")

    while True:
        try:
            with db_backup["backups"].watch(full_document="updateLookup") as stream:
                for change in stream:
                    if change.get("operationType") == "insert":
                        print("\nNovo backup detectado. Processando...")

                        inserted = ao_detectar_banco()
                        if inserted:            
                            db_backup.client.drop_database("backups-luminia")
                            print(f"Database apagado após processar.")

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

def replicate_collection(collection, collection_shadow):
    try:
        pipeline = [{"$match": {"operationType": {"$in": ["insert", "update"]}}}]
        with collection.watch(pipeline, full_document="updateLookup") as stream:
            for change in stream:
                op = change["operationType"]
                doc_id = change["documentKey"]["_id"]

                if op == "insert":
                    collection_shadow.insert_one(change["fullDocument"])
                    print(f"[INSERT] Documento {doc_id} replicado no Shadow.")
                elif op == "update":
                    updated_fields = change["updateDescription"]["updatedFields"]
                    collection_shadow.update_one(
                        {"_id": doc_id},
                        {"$set": updated_fields},
                        upsert=True
                    )
                    print(f"[UPDATE] Documento {doc_id} sincronizado no Shadow.")
    except Exception as e:
        print(f"Erro na thread de {collection.name}: {e}")

def update_user_data(data: dict):
    filtro = {}
    if "email" in data:
        filtro["email"] = data["email"]
    elif "name" in data:
        filtro["login.name"] = data["name"]
    else:
        print("Nenhum campo de identificação (email/nome) informado.")
        return None

    update_fields = {}
    for key, value in data.get("update", {}).items():
        update_fields[f"login.{key}"] = value
        if key in ["name", "role"]:
            update_fields[key] = value

    update_fields["login.modified_at"] = datetime.now(
        timezone(timedelta(hours=-3))
    ).isoformat(timespec='seconds')

    print(f"Filtro usado: {filtro}")
    print(f"Campos para atualizar: {update_fields}")

    result = collection_users.update_one(filtro, {"$set": update_fields})

    print(f"matched_count: {result.matched_count}")
    print(f"modified_count: {result.modified_count}")

    if result.matched_count == 0:
        print("Nenhum usuário encontrado com o filtro informado.")
        return None

    if result.modified_count == 0:
        print("Nenhum campo foi alterado (valores idênticos?).")

    print("Atualização concluída com sucesso.")
    return result

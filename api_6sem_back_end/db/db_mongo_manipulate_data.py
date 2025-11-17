from datetime import datetime, timedelta, timezone
from api_6sem_back_end.db.db_configuration import db_deleted, db_data

collection_deleted_users = db_deleted["deleted-users"]
collection_users = db_data["users"]

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
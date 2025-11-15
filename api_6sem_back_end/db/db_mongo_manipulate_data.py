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
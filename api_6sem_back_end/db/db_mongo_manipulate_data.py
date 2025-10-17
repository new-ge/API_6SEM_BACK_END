from datetime import datetime, timezone
from api_6sem_back_end.db.db_configuration import db_deleted, db_data

collection_deleted_users = db_deleted["deleted-users"]
collection_users = db_data["users"]

def delete_user(id_user: int):
    delete_user_doc = {
        "id_user": id_user,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec='seconds')
    }

    collection_deleted_users.insert_one(delete_user_doc)

    collection_users.update_one(
        {"agent_id": id_user},
        {
            "$set": {
                "department": None,
                "email": None,
                "login": None,
                "name": None,
                "role": None,
                "isActive": False
            }
        }
    )

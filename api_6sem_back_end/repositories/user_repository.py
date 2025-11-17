from bson import ObjectId
from datetime import datetime, timezone, timedelta
from api_6sem_back_end.db.db_configuration import db_data


def serialize_user(user):
    if not user:
        return None
    user["_id"] = str(user["_id"])
    return user


class UserRepository:

    @staticmethod
    def get_last_agent_id():
        last_user = db_data["users"].find_one(sort=[("agent_id", -1)])
        return last_user["agent_id"] if last_user else 0

    @staticmethod
    def create_user(user_data: dict):
        now = datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')
        user_data["created_at"] = now
        user_data["modified_at"] = now
        user_data["firstaccess"] = True

        last_id = UserRepository.get_last_agent_id()
        user_data["agent_id"] = last_id + 1

        result = db_data["users"].insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return serialize_user(user_data)

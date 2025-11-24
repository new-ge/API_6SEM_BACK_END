from api_6sem_back_end.db.db_configuration import db_data
from bson import ObjectId

collection = db_data["users"]

class UpdateRepository:
    @staticmethod
    def find_by_email_or_name(identifier: str):
        return collection.find_one({
            "$or": [
                {"email": identifier},
                {"name": identifier}
            ]
        })

    @staticmethod
    def update_user(agent_id: int, update_data: dict):
        result = collection.update_one(
            {"agent_id": agent_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    def find_by_agent_id(agent_id: int):
        return db_data["users"].find_one(
            {"agent_id": agent_id},
            {"name": 1}
        )
    
    @staticmethod
    def find_by_name_or_email(identifier: str):
        return db_data["users"].find_one({
            "$or": [
                {"name": identifier},
                {"email": identifier}
            ]
        })

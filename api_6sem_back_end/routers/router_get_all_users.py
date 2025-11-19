from fastapi import APIRouter, Depends
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/get-all", tags=["Get all"])
collection = db_data["users"]

@router.get("/get-all-users")
def get_all_users(payload=Depends(verify_token)):
    cursor = collection.find({}, {"agent_id": 1, "name": 1, "email": 1, "isActive": 1})
    users = []

    for doc in cursor:
        name = doc.get("name")
        email = doc.get("email")

        if doc.get("isActive") == True:

            users.append({
                "id": doc.get("agent_id"),
                "name": name,
                "email": email
            })

    return users
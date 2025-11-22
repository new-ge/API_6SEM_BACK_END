from fastapi import APIRouter, Depends
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/history", tags=["History"])
collection = db_data["history"]

@router.get("/get-all-logs")
def get_all_users():
    cursor = collection.find({}, {"audit_id": 1, "modified_by": 1, "modified_user": 1, "action": 1, "performed_at": 1})
    history = []

    for doc in cursor:
        history.append({
            "id": doc.get("audit_id"),
            "modified_by": doc.get("modified_by"),
            "modified_user": doc.get("modified_user"),
            "action": doc.get("action"),
            "performed_at": doc.get("performed_at")
        })

    return history
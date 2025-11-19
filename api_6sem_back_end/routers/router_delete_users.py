from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta
from api_6sem_back_end.db.db_mongo_manipulate_data import delete_users
from api_6sem_back_end.repositories.repository_login_security import verify_token 

router = APIRouter(prefix="/delete", tags=["Delete"])

@router.post("/delete-users")
def test_delete_users(agent_ids: list[int], payload=Depends(verify_token)):

    result = delete_users(agent_ids)
    return {
        "status": "OK",
        "timestamp": datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')
    }

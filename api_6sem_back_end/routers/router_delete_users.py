from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
from api_6sem_back_end.db.db_mongo_manipulate_data import delete_users 

router = APIRouter(prefix="/delete", tags=["Delete"])

@router.post("/delete-users")
def test_delete_users(agent_ids: list[int]):

    result = delete_users(agent_ids)
    return {
        "status": "OK",
        "deleted_ids": agent_ids,
        "result": result,
        "timestamp": datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds')
    }

from fastapi import APIRouter, Depends
from datetime import datetime, timezone, timedelta
from api_6sem_back_end.db.db_mongo_manipulate_data import delete_users, find_users_by_ids
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.utils.utils_logs import log_action 

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/delete-users")
@log_action("DELETE")
def delete_users_db(agent_ids: list[int], payload=Depends(verify_token)):

    users_to_delete = find_users_by_ids(agent_ids)
    deleted_names = [u["name"] for u in users_to_delete]

    delete_users(agent_ids)

    return {
        "status": "OK",
        "timestamp": datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds'),
        "deleted_names": deleted_names
    }
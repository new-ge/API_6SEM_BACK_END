from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.db.db_security import decrypt_data
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["Tickets"])

collection = db["tickets"]
collection.create_index("closed_at")

@router.get("/closed/average-time")
def average_time_closed_tickets():

    docs = list(collection.find({"closed_at": {"$ne": None}}, {"closed_at": 1, "created_at": 1}))

    if not docs:
        return {"average_duration_minutes": 0}

    diff_seconds_list = []
    for doc in docs:
        closed_at_str = decrypt_data(doc["closed_at"])
        created_at_str = decrypt_data(doc["created_at"])

        if not closed_at_str or closed_at_str.lower() == "none":
            continue
        if not created_at_str or created_at_str.lower() == "none":
            continue

        try:
            closed_at = datetime.fromisoformat(closed_at_str)
            created_at = datetime.fromisoformat(created_at_str)
        except ValueError:
            continue

        diff_seconds_list.append((closed_at - created_at).total_seconds())

    average_seconds = sum(diff_seconds_list) / len(diff_seconds_list)
    average_minutes = round(average_seconds / 60, 2)

    return {"average_duration_minutes": average_minutes}
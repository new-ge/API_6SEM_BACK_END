from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]
collection.create_index("priority")

@router.get("/priorities")
def get_priorities_by_ticket():
    pipeline = [
        {
            "$match": {
                "TicketId": {"$exists": True, "$ne": None},
                "priority": {"$exists": True, "$ne": None}
            }
        },
        {
            "$project": {
                "_id": 0,
                "TicketId": 1,
                "priority": 1
            }
        }
    ]
    
    result = collection.aggregate(pipeline)

    priorities = {doc["TicketId"]: doc["priority"] for doc in result}

    return priorities


@router.get("/test")
def test():
    cursor = collection.find({})
    tickets = list(cursor)
    return tickets

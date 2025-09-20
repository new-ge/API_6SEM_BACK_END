from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from collections import defaultdict

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]
collection.create_index("priority")

@router.get("/priorities")
def get_priorities_by_ticket():
    result = {}
    cursor = collection.find({})
    for ticket in cursor:
        ticket_id = ticket.get("TicketId")
        priority = ticket.get("priority")
        if ticket_id is not None and priority is not None:
            result[ticket_id] = priority
    return result

@router.get("/test")
def test():
    cursor = collection.find({})
    tickets = list(cursor)
    return tickets

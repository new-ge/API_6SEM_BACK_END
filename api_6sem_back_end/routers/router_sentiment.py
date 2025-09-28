from fastapi import APIRouter
from pydantic import BaseModel
from api_6sem_back_end.db.db_configuration import db  # <- Aqui está o conserto
from api_6sem_back_end.services.sentiment import classify_ticket_sentiment

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]  # Agora funciona

class TicketInput(BaseModel):
    ticket_id: int

@router.post("/sentiment")
def classify_sentiment(ticket: TicketInput):
    result = classify_ticket_sentiment(ticket.ticket_id)
    return result

from bson import ObjectId

@router.get("/sentiment1")
def classify_ticket_sentiment(ticket_id: int):
    print(f"Procurando ticket_id: {ticket_id}")
    ticket = collection.find_one({"ticket_id": ticket_id})
    print(f"Resultado da busca: {ticket}")
    
    if ticket:
        ticket["_id"] = str(ticket["_id"])
    
    return ticket

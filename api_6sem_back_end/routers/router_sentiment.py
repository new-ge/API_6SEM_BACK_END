from fastapi import APIRouter
from pydantic import BaseModel

from api_6sem_back_end.services.sentiment import classify_ticket_sentiment

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])

class TicketInput(BaseModel):
    ticket_id: int

@router.post("/")
def classify_sentiment(ticket: TicketInput):
    result = classify_ticket_sentiment(ticket.ticket_id)
    return result

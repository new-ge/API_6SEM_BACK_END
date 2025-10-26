from typing import Optional
from fastapi import APIRouter, Depends, Query
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.services.service_sentiment import ServiceSentiment
from api_6sem_back_end.utils.query_filter import Filtro
from api_6sem_back_end.db.de import db_data

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db_data["tickets"]

@router.post("/sentiment")
def classify_sentiment(
    payload=Depends(verify_token),
    filtro: Filtro = "",
    include_positive: Optional[bool] = Query(True)
):
    return ServiceSentiment.count_tickets_by_sentiment(filtro, include_positive, payload.get("role"))
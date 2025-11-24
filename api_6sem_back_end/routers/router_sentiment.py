from typing import Optional
from fastapi import APIRouter, Depends, Query
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.services.service_sentiment import ServiceSentiment
from api_6sem_back_end.utils.utils_query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/sentiment")
def classify_sentiment(
    payload=Depends(verify_token),
    filtro: Filtro = "",
    include_positive: Optional[bool] = Query(True)
):
    return ServiceSentiment.count_tickets_by_sentiment(filtro, include_positive, payload.get("role"))
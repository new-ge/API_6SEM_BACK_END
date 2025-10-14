from typing import Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.ml.train_sentiment import train_sentiment_model
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

@router.post("/sentiment")
def classify_sentiment(
    payload=Depends(verify_token),
    filtro: Filtro = "",
    include_positive: Optional[bool] = Query(False)
):
    return train_sentiment_model(filtro, include_positive=include_positive)
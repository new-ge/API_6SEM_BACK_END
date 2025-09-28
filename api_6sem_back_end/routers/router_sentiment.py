from fastapi import APIRouter
from pydantic import BaseModel
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.ml.train_sentiment import train_sentiment_model
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

@router.post("/sentiment")
def classify_sentiment(filtro: Filtro):
    return train_sentiment_model(filtro)
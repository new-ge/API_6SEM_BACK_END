from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.db.db_security import decrypt_data
from datetime import datetime

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]

@router.get("/opened/count")
def count_opened_tickets():
    count = collection.count_documents({"closed_at_dt": {"$in": [None, "None"]}})
    return {"opened_tickets": count}
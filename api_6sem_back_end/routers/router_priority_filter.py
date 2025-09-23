from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]

class Filtro(BaseModel):
    filtro: Dict[str, Any]

@router.post("/priorities")
def count_opened_tickets(filtro: Filtro):
    query_filter = {}
  
    query_filter["closed_at"] = { "$in": [None] }
    
    if filtro and filtro.filtro:
        for k, v in filtro.filtro.items():
            if v not in [None, "", [], {}]:
                query_filter[k] = v

    count = collection.count_documents(query_filter)
    return {"opened_tickets": count}

@router.get("/test")
def test():
    cursor = collection.find({})
    tickets = list(cursor)
    return tickets


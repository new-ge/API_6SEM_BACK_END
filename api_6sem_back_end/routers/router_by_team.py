from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from api_6sem_back_end.db.db_configuration import db

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

class Filtro(BaseModel):
    filtro: Dict[str, Any]

@router.post("/by-team/count")
def count_by_access_level(filtro: Filtro):
    query_filter = {"closed_at": None}

    if filtro and filtro.filtro:
        access_level = filtro.filtro.get("access_level")
        if access_level:
            query_filter["access_level"] = access_level

    count = collection.count_documents(query_filter)

    return {
        "access_level": query_filter.get("access_level"),
        "count": count
    }

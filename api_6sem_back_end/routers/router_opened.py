from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]
collection.create_index("closed_at")

@router.post("/opened/count")
def count_opened_tickets(filtro: Filtro):
    base_filter = {"closed_at": {"$in": [None]}}

    query_filter = build_query_filter(filtro.filtro, base_filter)

    count = collection.count_documents(query_filter)

    return {"opened_tickets": count}
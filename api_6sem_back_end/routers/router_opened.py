from fastapi import APIRouter, Depends
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db_data["tickets"]
collection.create_index("closed_at")

@router.post("/opened/count")
def count_opened_tickets(payload=Depends(verify_token), filtro: Filtro = ""):
    base_filter = {"closed_at": {"$in": [None]}}

    query_filter = build_query_filter(filtro, base_filter)

    count = collection.count_documents(query_filter)

    return {"opened_tickets": count}
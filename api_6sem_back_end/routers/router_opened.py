from fastapi import APIRouter, Depends
from api_6sem_back_end.db.db_configuration import MongoConnection
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = MongoConnection.get_db("bd6sem-luminia")["tickets"]
collection.create_index("closed_at")

@router.post("/opened/count")
def count_opened_tickets(payload=Depends(verify_token), filtro: Filtro = ""):
    base_filter = {"closed_at": {"$in": [None]}}
    
    if (payload.get("role") != "Gestor"):
        levels_map = {
            "N1": ["N1"],
            "N2": ["N1", "N2"],
            "N3": ["N1", "N2", "N3"]
        }

        allowed_levels = levels_map.get(payload.get("role").upper())

        base_filter = {
            "closed_at": {"$in": [None]},
            "access_level": {"$in": allowed_levels}
        }

    query_filter = build_query_filter(filtro, base_filter)

    count = collection.count_documents(query_filter)

    return {"opened_tickets": count}
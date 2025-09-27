from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]  

@router.post("/closed/exceeded-sla")
def tickets_exceeded_sla(filtro: Filtro):
    base_filter = {"closed_at": {"$ne": None}}

    query_filter = build_query_filter(filtro, base_filter)

    pipeline = [
        {"$match": query_filter},
        {
            "$project": {
                "sla_target_minutes": "$sla.target_minutes",
                "tempo_total_minutes": {
                    "$divide": [
                        {"$subtract": [
                            {"$toDate": "$closed_at"},
                            {"$toDate": "$created_at"}
                        ]},
                        1000 * 60
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "total_chamados": {"$sum": 1},
                "sla_exceeded": {
                    "$sum": {
                        "$cond": [
                            {"$gt": ["$tempo_total_minutes", "$sla_target_minutes"]},
                            1,
                            0
                        ]
                    }
                }
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    if not result:
        return {"sla_exceeded": 0}

    return {
        "sla_exceeded": result[0]["sla_exceeded"]
    }

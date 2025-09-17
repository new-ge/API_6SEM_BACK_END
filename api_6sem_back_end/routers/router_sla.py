from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db  

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]  

@router.get("/closed/exceeded-sla")
def tickets_exceeded_sla():
    pipeline = [
        {"$match": {"closed_at": {"$ne": None}}},
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
                "total_excedidos": {
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
        return {"total_excedidos": 0}

    return {
        "total_excedidos": result[0]["total_excedidos"]
    }

from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])

collection = db["tickets"]
collection.create_index("closed_at")

@router.post("/closed/average-time")
def average_time_closed_tickets(filtro: Filtro):
    base_filter = {"closed_at": {"$ne": None}}

    if hasattr(filtro, "role") and filtro.role and filtro.role != "Gestor":
        role = filtro.role.upper().strip()

        role_hierarchy = {
            "N3": ["N1", "N2", "N3"],
            "N2": ["N1", "N2"],
            "N1": ["N1"]
        }
        
        roles_visiveis = role_hierarchy.get(role, ["N1"])

        base_filter["access_level"] = {"$in": roles_visiveis}

    query_filter = build_query_filter(filtro, base_filter)
    pipeline = [
        {"$match": query_filter},
        {
            "$project": {
                "diffInSeconds": {
                    "$divide": [
                        {"$subtract": [
                            "$closed_at",
                            "$created_at"
                        ]},
                        1000
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "average_duration_seconds": {"$avg": "$diffInSeconds"}
            }
        }
    ]

    result = list(collection.aggregate(pipeline))

    if not result:
        return {"average_duration_minutes": 0}

    average_seconds = result[0]["average_duration_seconds"]
    average_minutes = round(average_seconds / 60, 2)

    return {"average_duration_minutes": average_minutes}
from fastapi import APIRouter, Depends
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro
from api_6sem_back_end.db.db_configuration import db_data

router = APIRouter(prefix="/tickets", tags=["Tickets"])

collection = db_data["tickets"]

@router.post("/closed/average-time")
def average_time_closed_tickets(payload=Depends(verify_token), filtro: Filtro = ""):
    base_filter = {"closed_at": {"$ne": None}}

    if payload.get("role") != "Gestor":
        user_access = payload.get("role")

        levels_hierarchy = ["N1", "N2", "N3"]

        if user_access in levels_hierarchy:
            idx = levels_hierarchy.index(user_access)
            allowed_levels = levels_hierarchy[: idx + 1]
            base_filter["access_level"] = {"$in": allowed_levels}

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
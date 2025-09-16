from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db

router = APIRouter(prefix="/tickets", tags=["Tickets"])

collection = db["tickets"]
collection.create_index("closed_at")

@router.get("/closed/average-time")
async def average_time_closed_tickets():
    pipeline = [
        {"$match": {"ClosedAt": {"$ne": None}}},
        {
            "$project": {
                "diffInSeconds": {
                    "$divide": [
                        {"$subtract": [
                            {"$toDate": "$closed_at"},
                            {"$toDate": "$created_at"}
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

    result = await collection.aggregate(pipeline).to_list(length=1)

    if not result:
        return {"average_duration_minutes": 0}

    average_seconds = result[0]["average_duration_seconds"]
    average_minutes = round(average_seconds / 60, 2)

    return {"average_duration_minutes": average_minutes}
from api_6sem_back_end.db import collection
from datetime import datetime


class TicketRepository:
    @staticmethod
    async def count_by_period(start_date: datetime, end_date: datetime):
        pipeline = [
            {
                "$match": {
                    "created_at": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                }
            },
            {
                "$group": {
                    "_id": {
                        "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.day": 1}}
        ]

        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

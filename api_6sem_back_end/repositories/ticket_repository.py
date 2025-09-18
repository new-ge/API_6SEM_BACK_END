from api_6sem_back_end.db.db_configuration import db
from datetime import datetime

collection = db["tickets"]

class TicketRepository:
    @staticmethod
    def count_by_period(start_date: datetime, end_date: datetime):
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
                    "_id": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}},
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id.day": 1}}
        ]

        cursor = collection.aggregate(pipeline)
        return list(cursor)
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

collection = db["tickets"]

class TicketService:
    @staticmethod
    def count_tickets_by_month(filtro: Filtro):
        query_filter = build_query_filter(filtro)

        pipeline = [
            {"$match": query_filter},
            {
                "$group": {
                    "_id": {"$month": "$created_at"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "month": {
                        "$cond": [
                            {"$lt": ["$_id", 10]},
                            {"$concat": ["0", {"$toString": "$_id"}]},
                            {"$toString": "$_id"}
                        ]
                    },
                    "count": 1
                }
            },
            {"$sort": {"month": 1}}
        ]

        result = list(collection.aggregate(pipeline))
        return {doc["month"]: doc["count"] for doc in result}

    @staticmethod
    def get_open_tickets_volume_by_level(user_level: str):

        levels_map = {
            "N1": ["N1"],
            "N2": ["N1", "N2"],
            "N3": ["N1", "N2", "N3"]
        }

        allowed_levels = levels_map.get(user_level.upper(), [])

        query_filter = {
            "closed_at": None,
            "access_level": {"$in": allowed_levels}
        }

        volume = collection.count_documents(query_filter)

        return {
            "volume": volume
        }

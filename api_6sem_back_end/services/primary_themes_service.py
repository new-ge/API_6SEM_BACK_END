from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

collection = db["tickets"]

class TicketService:
    @staticmethod
    def count_tickets_by_category(filtro: Filtro):
        query_filter = build_query_filter(filtro.filtro)

        pipeline = [
            {"$match": query_filter},
            {
                "$group": {
                    "_id": "$category",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "categoria": "$_id",
                    "count": 1
                }
            },
            {"$sort": {"count": -1}}
        ]

        result = list(collection.aggregate(pipeline))
        return result

from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro
from datetime import datetime
from api_6sem_back_end.db.de import db_data

collection = db_data["tickets"]

class ServiceTicketsByMonth:
    @staticmethod
    def count_tickets_by_month(filtro: Filtro, role: str):
        if (role != "Gestor"):
            levels_map = {
                "N1": ["N1"],
                "N2": ["N1", "N2"],
                "N3": ["N1", "N2", "N3"]
            }

            allowed_levels = levels_map.get(role.upper(), [])

            base_filter = {
                "access_level": {"$in": allowed_levels}
            }

            query_filter = build_query_filter(filtro, base_filter)
            
        else:
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
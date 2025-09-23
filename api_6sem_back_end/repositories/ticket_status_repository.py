import re
from api_6sem_back_end.db.db_configuration import db

collection = db["tickets"]

class TicketStatusRepository:
    @staticmethod
    def count_by_status(filtro: dict):
        query_filter = {
            "$or": [
                {"closed_at": None},
                {"closed_at": {"$exists": False}}
            ]
        }

        if filtro:
            for k, v in filtro.items():
                if v not in [None, "", [], {}]:
                    if isinstance(v, str):
                        query_filter[k] = re.compile(f"^{v.strip()}$", re.IGNORECASE)
                    else:
                        query_filter[k] = v

        #print(">>> Query Filter usado:", query_filter)
        matched_count = collection.count_documents(query_filter)
        #print(">>> Quantidade de documentos encontrados antes do group:", matched_count)

        pipeline = [
            {"$match": query_filter},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        cursor = collection.aggregate(pipeline)
        result = list(cursor)

        #print(">>> Resultado do aggregate:", result)

        return result

from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.utils.query_filter import build_query_filter, Filtro

collection = db_data["tickets"]

class ServiceSentiment:
    @staticmethod
    def count_tickets_by_sentiment(filtro: Filtro, include_positive: bool):
        query_filter = build_query_filter(filtro)

        pipeline = [
            {"$match": query_filter},
            {
                "$group": {
                    "_id": "$sentiment",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "sentimento": "$_id",
                    "count": 1
                }
            }
        ]

        result = list(collection.aggregate(pipeline))

        sentimentos_count = {"negative": 0, "positive": 0}

        for r in result:
            sentimento_upper = r["sentimento"].lower()
            if sentimento_upper in sentimentos_count:
                sentimentos_count[sentimento_upper] = r["count"]

        if not include_positive:
            return {"negative": sentimentos_count["negative"]}
        else:
            return sentimentos_count
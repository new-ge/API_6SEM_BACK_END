from datetime import datetime
import gc
import json
from flair.models import TextClassifier
from flair.data import Sentence
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import Filtro, build_query_filter
import api_6sem_back_end.models.model_store as store
from cachetools import LRUCache

collection = db["tickets"]
collection.create_index("description")
classifier = TextClassifier.load("sentiment-fast")

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def train_sentiment_model(filtro: Filtro = None):
    if not hasattr(store, "sentiment_cache") or not isinstance(store.sentiment_cache, dict):
        store.sentiment_cache = LRUCache(maxsize=3)

    query_filter = build_query_filter(filtro) if filtro else {}
    cache_key = json.dumps(query_filter, sort_keys=True, default=json_serializer)

    if cache_key in store.sentiment_cache:
        return store.sentiment_cache[cache_key]

    pipeline = [
        {"$match": query_filter},
        {"$group": {"_id": "$description", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "description": "$_id", "count": 1}},
        {"$sort": {"count": -1}}
    ]

    cursor = collection.aggregate(pipeline, allowDiskUse=True)

    resultado = {"positive": 0, "negative": 0, "neutral": 0}

    batch_size = 64
    sentences, counts = [], []

    for row in cursor:
        desc = row["description"].strip()
        if not desc:
            continue

        sentences.append(Sentence(desc))
        counts.append(row["count"])

        if len(sentences) >= batch_size:
            classifier.predict(sentences, mini_batch_size=batch_size)
            for sentence, count in zip(sentences, counts):
                label = sentence.labels[0].value
                if label == "POSITIVE":
                    resultado["positive"] += count
                elif label == "NEGATIVE":
                    resultado["negative"] += count
                else:
                    resultado["neutral"] += count
            sentences.clear()
            counts.clear()
            gc.collect()

    if sentences:
        classifier.predict(sentences, mini_batch_size=batch_size)
        for sentence, count in zip(sentences, counts):
            label = sentence.labels[0].value
            if label == "POSITIVE":
                resultado["positive"] += count
            elif label == "NEGATIVE":
                resultado["negative"] += count
            else:
                resultado["neutral"] += count
        sentences.clear()
        counts.clear()
        gc.collect()

    store.sentiment_cache[cache_key] = resultado
    return resultado

from datetime import datetime
import json
from cachetools import LRUCache
import pandas as pd
from prophet import Prophet
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.utils.query_filter import Filtro, build_query_filter
import api_6sem_back_end.models.model_store as store

collection = db_data["tickets"]
collection.create_index("created_at")

def json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def create_prophet_instance():
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.3,
        seasonality_prior_scale=0.1,
        mcmc_samples=0
    )
    model.add_seasonality(name="monthly", period=30.5, fourier_order=5)
    return model


def train_model(filtro: Filtro = None, train_until: str = None):
    if not hasattr(store, "prophet_cache") or not isinstance(store.prophet_cache, dict):
        store.prophet_cache = LRUCache(maxsize=3)

    query_filter = build_query_filter(filtro)
    cache_key = json.dumps(query_filter, sort_keys=True, default=json_serializer)

    if cache_key in store.prophet_cache:
        df_grouped = store.prophet_cache[cache_key]
    else:
        pipeline = [
            {"$match": query_filter},
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"},
                    },
                    "y": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "ds": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": 1,
                        }
                    },
                    "y": 1,
                }
            },
            {"$sort": {"ds": 1}},
        ]

        cursor = collection.aggregate(pipeline)
        df_grouped = pd.DataFrame.from_records(cursor)

        if df_grouped.empty:
            return None, None

        df_grouped["ds"] = pd.to_datetime(df_grouped["ds"])
        df_grouped = df_grouped.sort_values("ds").reset_index(drop=True)

        store.prophet_cache[cache_key] = df_grouped

    if train_until:
        df_grouped = df_grouped[df_grouped["ds"] <= pd.to_datetime(train_until)]

    model = create_prophet_instance()
    model.fit(df_grouped)

    return model, df_grouped

def get_model():
    return store.prophet_cache

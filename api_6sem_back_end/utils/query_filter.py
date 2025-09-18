from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime

class Filtro(BaseModel):
    filtro: Dict[str, Any]

def build_query_filter(filtro, base_filter=None):
    query_filter = base_filter.copy() if base_filter else {}

    if filtro:
        for k, v in filtro.items():
            if v in [None, "", [], {}]:
                continue

            if k in ["created_at_start", "created_at_end"]:
                if isinstance(v, (int, float)):
                    v = datetime.fromtimestamp(v / 1000)

                query_filter.setdefault("created_at", {})
                if k == "created_at_start":
                    query_filter["created_at"]["$gte"] = v
                elif k == "created_at_end":
                    query_filter["created_at"]["$lte"] = v

            elif isinstance(v, list):
                query_filter[k] = {"$in": v}

    return query_filter

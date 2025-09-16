from fastapi import APIRouter, Query
from api_6sem_back_end.db.db_configuration import db
from collections import defaultdict
from typing import Optional

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]
collection.create_index("tag")

@router.get("/tags")
def get_all_tags():
    tag_counts = defaultdict(int)
    cursor = collection.find({})
    for ticket in cursor:
        tags = ticket.get("tag", [])
        if isinstance(tags, list):
            for tag in tags:
                tag_counts[tag] += 1
    return dict(tag_counts)
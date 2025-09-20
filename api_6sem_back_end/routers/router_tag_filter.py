from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]
collection.create_index("tag")

@router.get("/tags")
def get_all_tags():
    
    pipeline = [
        {"$unwind": "$tag"},  
        {"$group": {"_id": "$tag", "count": {"$sum": 1}}},  
        {"$sort": {"count": -1}}  
    ]
    
    result = list(collection.aggregate(pipeline))
    
    
    tag_counts = {item["_id"]: item["count"] for item in result}
    
    return tag_counts

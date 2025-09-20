from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from collections import defaultdict
import logging

router = APIRouter(prefix="/tickets", tags=["tickets"])
collection = db["tickets"]
collection.create_index("tag")

logging.basicConfig(level=logging.DEBUG)

@router.get("/tags")
def get_all_tags():
    tag_counts = defaultdict(int)
    logging.debug("Iniciando a consulta ao MongoDB...")
    cursor = collection.find({})
    
    for ticket in cursor:
        logging.debug(f"Processando ticket: {ticket.get('_id')}")
        tags = ticket.get("tag", [])
        if isinstance(tags, list):
            for tag in tags:
                tag_counts[tag] += 1
    logging.debug("Consulta finalizada.")
    return dict(tag_counts)



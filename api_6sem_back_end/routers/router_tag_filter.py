from fastapi import APIRouter, Query
from api_6sem_back_end.db import collection
from typing import Optional, Dict
from collections import defaultdict


router = APIRouter(prefix="/chamados", tags=["Chamados"])

TAG_FIELDS = [
    "CompanyId",
    "ProductId",
    "CategoryId",
    "SubcategoryId",
    "AssignedAgentId",
    "CreatedByUserId",
    "SLAPlanId",
    "CurrentStatusId",
    "Channel",
    "Device"
]

@router.get("/tags-por-prioridade")
async def get_tags_por_prioridade(priority: Optional[int] = Query(None, description="Filtrar por PriorityId")):
    """
    Retorna a contagem de valores por tag nos chamados, filtrando por prioridade (se informada).
    """
    match_query = {}
    if priority is not None:
        match_query["PriorityId"] = priority

    cursor = collection.find(match_query)
    tag_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    async for ticket in cursor:
        for tag in TAG_FIELDS:
            value = ticket.get(tag)
            if value is not None:
                tag_counts[tag][str(value)] += 1  

    
    result = {tag: dict(values) for tag, values in tag_counts.items()}
    return result

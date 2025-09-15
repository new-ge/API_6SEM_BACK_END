from fastapi import APIRouter, Query
from api_6sem_back_end.db import collection
from typing import Optional, Dict
from collections import defaultdict

router = APIRouter(prefix="/chamados", tags=["Chamados"])

# Atualize os campos conforme os nomes REAIS no MongoDB
TAG_FIELDS = [
    "product",
    "category",
    "sub_category",
    "status",
    "tag",         # Isso é uma lista
    "priority",
    "sla.name"     # Nested field (iremos tratar separadamente)
]

@router.get("/tags-por-prioridade")
async def get_tags_por_prioridade(priority: Optional[str] = Query(None, description="Filtrar por prioridade")):
    """
    Retorna a contagem de valores por tag nos chamados, filtrando por prioridade (se informada).
    """
    match_query = {}
    if priority is not None:
        match_query["priority"] = priority

    cursor = collection.find(match_query)
    tag_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    async for ticket in cursor:
        for tag in TAG_FIELDS:
            if "." in tag:
                # Tratando campo aninhado como "sla.name"
                parent, child = tag.split(".")
                value = ticket.get(parent, {}).get(child)
            else:
                value = ticket.get(tag)

            # Se for lista (como "tag": ["Revisar", "Solicitação"])
            if isinstance(value, list):
                for item in value:
                    tag_counts[tag][str(item)] += 1
            elif value is not None:
                tag_counts[tag][str(value)] += 1

    result = {tag: dict(values) for tag, values in tag_counts.items()}
    return result

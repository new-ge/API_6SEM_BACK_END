from fastapi import APIRouter
from fastapi import APIRouter, Query
from api_6sem_back_end.db import collection
from collections import defaultdict
from typing import Optional

router = APIRouter(prefix="/chamados", tags=["Chamados"])

@router.get("/tags")
async def get_all_tags():
    tag_counts = defaultdict(int)
    cursor = collection.find({})
    async for ticket in cursor:
        tags = ticket.get("tag", [])
        if isinstance(tags, list):
            for tag in tags:
                tag_counts[tag] += 1
    return dict(tag_counts)


@router.get("/teste-docs")
async def teste_docs():
    cursor = collection.find().limit(5)
    docs = []
    async for doc in cursor:
        docs.append(doc)
    return docs

@router.get("/inserir-teste")
async def inserir_teste():
    ticket = {
        "ticket_id": 1,
        "category": "Dados",
        "priority": "Média",
        "tag": ["Solicitação", "RH", "Duplicado"],
        "description": "Erro no cálculo da remuneração variável de agosto."
    }
    result = await collection.insert_one(ticket)
    return {"inserted_id": str(result.inserted_id)}

@router.get("/listar-tickets")
async def listar_tickets():
    cursor = collection.find().limit(10)
    tickets = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Converter ObjectId para string para JSON
        tickets.append(doc)
    return tickets

@router.get("/tags-por-prioridade")
async def tags_por_prioridade(priority: Optional[str] = Query(None, description="Filtrar por prioridade")):
    match_query = {}
    if priority:
        match_query["priority"] = priority
    
    cursor = collection.find(match_query)
    tag_counts = defaultdict(int)
    
    async for doc in cursor:
        tags = doc.get("tag", [])
        for tag in tags:
            tag_counts[tag] += 1

    return dict(tag_counts)
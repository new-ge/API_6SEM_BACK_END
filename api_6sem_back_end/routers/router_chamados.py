from fastapi import APIRouter
from api_6sem_back_end.db import collection  # agora vem do módulo separado

router = APIRouter(prefix="/chamados", tags=["Chamados"])

@router.get("/abertos/count")
async def count_chamados_abertos():
    filter_query = {"ClosedAt": None}
    count = await collection.count_documents(filter_query)
    return {"chamados_abertos": count}

from fastapi import APIRouter
from api_6sem_back_end.main import collection  # ajuste esse import conforme o caminho real

router = APIRouter(prefix="/chamados", tags=["Chamados"])

@router.get("/abertos/count")  # <-- corrigido aqui
async def count_chamados_abertos():
    filter_query = {"data_fechamento": {"$exists": False}}
    count = await collection.count_documents(filter_query)
    return {"chamados_abertos": count}

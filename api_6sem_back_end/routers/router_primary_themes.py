from fastapi import APIRouter, Query
from typing import Optional
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.services.primary_themes_service import TicketService
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

@router.get("/primary-themes")
async def principais_temas(categoria: Optional[str] = Query(None)):
    filtro = Filtro(filtro={})
    if categoria:
        filtro.filtro = {"categoria": categoria}
    

    result = TicketService.count_tickets_by_category(filtro)
    return result

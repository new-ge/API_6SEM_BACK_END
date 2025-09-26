from fastapi import APIRouter, Query
from typing import Optional
from api_6sem_back_end.services.primary_themes_service import TicketService
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/primary-themes")
async def principais_temas(filtro: Filtro):
    return TicketService.count_tickets_by_category(filtro)


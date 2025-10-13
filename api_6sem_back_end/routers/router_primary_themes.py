from fastapi import APIRouter, Depends
from api_6sem_back_end.services.primary_themes_service import TicketService
from api_6sem_back_end.utils.query_filter import Filtro
from api_6sem_back_end.repositories.repository_login_security import verify_token

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/primary-themes")
async def principais_temas(payload=Depends(verify_token), filtro: Filtro = ""):
    return TicketService.count_tickets_by_category(filtro)


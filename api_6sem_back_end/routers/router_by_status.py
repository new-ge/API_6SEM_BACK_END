from fastapi import APIRouter
from api_6sem_back_end.models.filter import Filtro
from api_6sem_back_end.services.ticket_status_service import TicketStatusService

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/count-by-status")
def count_tickets(filtro: Filtro):
    return TicketStatusService.count_tickets_by_status(filtro.filtro)

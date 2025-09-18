from fastapi import APIRouter
from api_6sem_back_end.services.ticket_service import TicketService
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

@router.post("/by-period")
def count_tickets(filtro: Filtro):
    return TicketService.count_tickets_by_month(filtro)
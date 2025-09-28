from fastapi import APIRouter
from api_6sem_back_end.services.service_get_forecast import get_forecast
from api_6sem_back_end.services.ticket_service import TicketService
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db["tickets"]

@router.post("/by-period")
def count_tickets(filtro: Filtro):
    result_tickets = TicketService.count_tickets_by_month(filtro)
    result_forecast = get_forecast(filtro)

    return {
        "tickets": result_tickets,
        "forecast": result_forecast
    }
from fastapi import APIRouter
from typing import Dict, Any
from api_6sem_back_end.services.ticket_service import TicketService
from api_6sem_back_end.models.ticket import TicketPeriod

router = APIRouter(prefix="/tickets", tags=["tickets"])

@router.get("/by-period", response_model=Dict[str, Any])
def count_tickets(request: TicketPeriod):
    return TicketService.count_tickets_by_period(
        start_date=request.start_date,
        end_date=request.end_date
    )

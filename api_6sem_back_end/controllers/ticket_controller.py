from fastapi import APIRouter
from typing import Dict, Any
from services.ticket_service import TicketService
from models.ticket import TicketPeriod

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/count", response_model=Dict[str, Any])
def count_tickets(request: TicketPeriod):
    return TicketService.count_tickets_by_period(
        start_date=request.start_date,
        end_date=request.end_date
    )
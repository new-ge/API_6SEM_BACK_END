from fastapi import APIRouter, Query
from api_6sem_back_end.services.ticket_service import TicketService

router = APIRouter()

@router.get("/open-tickets/volume")
async def get_open_tickets_volume(user_level: str = Query(..., description="User access level: N1, N2 or N3")):
    result = TicketService.get_open_tickets_volume_by_level(user_level)
    return result

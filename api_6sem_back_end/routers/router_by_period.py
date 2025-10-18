from typing import Optional
from fastapi import APIRouter, Depends, Query
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.services.service_get_forecast import ServiceForecast
from api_6sem_back_end.services.service_tickets_by_month import ServiceTicketsByMonth
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.utils.query_filter import Filtro

router = APIRouter(prefix="/tickets", tags=["Tickets"])
collection = db_data["tickets"]

@router.post("/by-period")
def count_tickets(
    payload=Depends(verify_token),
    filtro: Filtro = "",
    include_forecast: Optional[bool] = Query(True)
):
    print(payload.get("role"))


    result_tickets = ServiceTicketsByMonth.count_tickets_by_month(filtro, payload.get("role"))

    volume_tickets = sum(result_tickets.values())


    result_forecast = None
    if include_forecast:
        result_forecast = get_forecast(filtro, payload.get("role"))
        volume_forecast = sum(result_forecast.values())

    return {
        "tickets": result_tickets,
        "volume tickets": volume_tickets,
        "forecast": result_forecast,
        "volume_forecast": volume_forecast

    }
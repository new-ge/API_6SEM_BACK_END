from pydantic import BaseModel
from datetime import datetime

class TicketResponse(BaseModel):
    TicketId: int
    Title: str
    CreatedAt: datetime
    FirstResponseAt: datetime
    TempoResposta: str
    ClosedAt: datetime
    TempoFechamento: str
    PriorityId: int
    CurrentStatusId: int


class  TicketPeriod(BaseModel):
    start_date: datetime
    end_date: datetime

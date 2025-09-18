from datetime import datetime
from api_6sem_back_end.repositories.ticket_repository import TicketRepository

class TicketService:
    @staticmethod
    def count_tickets_by_period(start_date: datetime, end_date: datetime):
        result = TicketRepository.count_by_period(start_date, end_date)

        counts_day = {r["_id"]["day"]: r["count"] for r in result}
        total_count = sum(counts_day.values())

        return {
            "total": total_count,
            "by_day": counts_day
        }

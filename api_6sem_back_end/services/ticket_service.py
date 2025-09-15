from datetime import datetime
from collections import defaultdict
from api_6sem_back_end.repositories.ticket_repository import TicketRepository

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f0"

class TicketService:
    @staticmethod
    def count_tickets_by_period(start_date: datetime, end_date: datetime):
        tickets = TicketRepository.get_all()
        
        counts_day = defaultdict(int)
        total_count = 0
        
        for t in tickets:
            created_at = datetime.strptime(t["CreatedAt"], DATETIME_FORMAT)
            if start_date <= created_at <= end_date:
                total_count += 1
                
                day_key = created_at.strftime("%Y-%m-%d")
                counts_day[day_key] += 1
        
        return {
            "total": total_count,
            "by_day": dict(counts_day),
        }


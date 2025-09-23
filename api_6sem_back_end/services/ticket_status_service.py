from api_6sem_back_end.repositories.ticket_status_repository import TicketStatusRepository

class TicketStatusService:
    @staticmethod
    def count_tickets_by_status(filtro: dict):
        result = TicketStatusRepository.count_by_status(filtro)

        # Constrói dicionário por status
        by_status = {r["_id"]: r["count"] for r in result}
        total_count = sum(by_status.values())

        return {
            "total": total_count,
            "by_status": by_status
        }

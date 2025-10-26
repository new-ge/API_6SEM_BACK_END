from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.db.de import db_data
collection = db_data["tickets"]

class TicketRepository:
    @staticmethod
    def get_all():
        return list(collection.find())

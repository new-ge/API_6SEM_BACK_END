from api_6sem_back_end.db.db_configuration import db

collection = db["tickets"]

class TicketRepository:
    @staticmethod
    def get_all():
        return list(collection.find())

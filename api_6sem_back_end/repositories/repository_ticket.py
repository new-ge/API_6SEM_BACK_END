from api_6sem_back_end.db.db_configuration import MongoConnection

collection = MongoConnection.get_db("bd6sem-luminia")["tickets"]

class TicketRepository:
    @staticmethod
    def get_all():
        return list(collection.find())

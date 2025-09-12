#from api_6sem_back_end.db.mongodb import db
collection = db["Collection name"] #provisório mudar para o certo depois

class TicketRepository:
    @staticmethod
    def get_all():
        return list(collection.find())

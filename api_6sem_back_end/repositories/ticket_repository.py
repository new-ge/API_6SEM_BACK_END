#from app.database.mongo import db
#Import da conexão com o banco ajustar posteriormente

collection = db["Collectiion name"]  #

class TicketRepository:
    @staticmethod
    def get_all():
        return list(collection.find())

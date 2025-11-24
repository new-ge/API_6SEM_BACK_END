from api_6sem_back_end.db.db_configuration import db_data

class LogsRepository:
    @staticmethod
    def get_last_audit_id():
        last_log = db_data["history"].find_one(sort=[("audit_id", -1)])
        return last_log["audit_id"] if last_log else 0
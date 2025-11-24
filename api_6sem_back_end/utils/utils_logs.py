from datetime import datetime, timedelta, timezone
import functools
import inspect
from bson import ObjectId
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.repositories.repository_create_logs import LogsRepository

collection = db_data["history"]

def fix_objectid(obj):
    if isinstance(obj, dict):
        return {k: fix_objectid(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [fix_objectid(v) for v in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    return obj

def save_log(action, modified_by, modified_user=None):
    log_entry = {
        "audit_id": LogsRepository.get_last_audit_id() + 1,
        "action": action,
        "modified_user": modified_user,
        "modified_by": modified_by,
        "performed_at": datetime.now(timezone(timedelta(hours=-3))).isoformat(timespec='seconds'),
    }

    collection.insert_one(log_entry)


def log_action(operation: str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):

            result = (
                await func(*args, **kwargs)
                if inspect.iscoroutinefunction(func)
                else func(*args, **kwargs)
            )

            token_data = kwargs.get("payload", {})

            modified_by = (
                token_data.get("username")
                or token_data.get("email")
                or token_data.get("name")
                or "unknown"
            )

            modified_user = None

            if "user" in result and isinstance(result["user"], dict):
                modified_user = (
                    result["user"].get("name")
                    or result["user"].get("username")
                )

            elif "deleted_names" in result:
                modified_user = ", ".join(result["deleted_names"])

            save_log(
                action=operation,
                modified_by=modified_by,
                modified_user=modified_user
            )

            return fix_objectid(result)

        return wrapper
    return decorator
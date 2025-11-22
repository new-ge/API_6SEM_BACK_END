from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.repositories.repository_login_security import create_jwt_token
from api_6sem_back_end.utils.utils_logs import save_log

router = APIRouter(prefix="/login", tags=["Login"])
collection = db_data["users"]

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/validate-login")
def validate_login(login_request: LoginRequest):
    try:
        if not login_request.username or not login_request.password:
            return None

        pipeline = [
            {
                "$match": {
                    "login.username": login_request.username,
                    "login.password": login_request.password
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "username": "$login.username",
                    "role": "$role",
                    "name": "$name",
                    "firstaccess": "$firstaccess"
                }
            }
        ]

        result = list(collection.aggregate(pipeline))

        if not result:
            return False

        user = result[0]

        if user.get("firstaccess", False) is True:
            return {
                "firstaccess": True,
                
            }
        
        save_log("LOGIN", modified_by=result[0]["name"])
        token = create_jwt_token(user["name"], user["role"])

        return {
            "token": token,
            "role": user["role"],
            "name": user["name"],
            "username": user["username"],
            "firstaccess": False
        }

    except Exception as e:
        raise Exception(f"Erro ao validar login: {str(e)}")


class FirstAccessPayload(BaseModel):
    new_password: str

@router.put("/complete-first-access/{username}")
def complete_first_access(username: str, payload: FirstAccessPayload):
    result = collection.update_one(
        {"login.username": username},
        {
            "$set": {
                "firstaccess": False,
                "login.password": payload.new_password,
                "modified_at": datetime.now()
            }
        }
    )

    if result.modified_count == 0:
        return {"success": False, "message": "Usuário não encontrado"}

    return {"success": True}

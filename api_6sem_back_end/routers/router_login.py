from fastapi import APIRouter
from pydantic import BaseModel
from api_6sem_back_end.db.db_configuration import db_data
from api_6sem_back_end.repositories.repository_login_security import create_jwt_token

router = APIRouter(prefix="/login", tags=["Login"])
collection = db_data["users"]

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/validate-login")
def validate_login(login_request: LoginRequest):
    try:
        if login_request.username == "" and login_request.password == "":
            return None
        else:
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
                        "username": {"$getField": {"field": "username", "input": "$login"}},
                        "role": "$role",
                        "name": "$name"
                    }
                }
              ]
            result = list(collection.aggregate(pipeline))
            if result:
                token = create_jwt_token(result[0]["username"], result[0]["role"])
                role = result[0]["role"]
                return {"token": token, "role": role, "name": result[0]["name"], "username": result[0]["username"]}
            else:
                print("Não encontrado!")
                return False
            
    except:
        raise Exception
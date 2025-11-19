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
def validate_login(username, password):
    try:
        if username == "" and password == "":
            return None
        else:
            pipeline = [
                {
                    "$match": {
                        "login.username": username,
                        "login.password": password
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "username": {"$getField": {"field": "username", "input": "$login"}},
                        "role": "$role"
                    }
                }
              ]
            result = list(collection.aggregate(pipeline))
            if result:
                token = create_jwt_token(result[0]["username"], result[0]["role"])
                return token
            else:
                print("Não encontrado!")
                return False
            
    except:
        raise Exception
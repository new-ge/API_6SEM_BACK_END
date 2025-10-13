from fastapi import APIRouter
from api_6sem_back_end.db.db_configuration import db
from api_6sem_back_end.repositories.repository_login_security import create_jwt_token, verify_token

router = APIRouter(prefix="/login", tags=["Login"])
collection = db["users"]

@router.post("/validate-login")
def validate_login(username, password):
    try:
        if username == "" and password == "":
            print("⚠️ Campos vazios — nenhuma busca feita.")
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
            print(result)
            if result:
                token = create_jwt_token(result[0]["username"], result[0]["role"])
                print(token)
                return token
            else:
                print("Não encontrado!")
        

    except:
        raise Exception
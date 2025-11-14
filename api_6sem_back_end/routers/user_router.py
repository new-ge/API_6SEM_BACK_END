from fastapi import APIRouter, Query
from api_6sem_back_end.db.db_mongo_manipulate_data import collection_users

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/find")
def find_user(
    email: str = Query(None, description="E-mail do usuário"),
    name: str = Query(None, description="Nome do usuário")
):
    
    
    filtro = {}
    if email:
        filtro["email"] = email
    elif name:
        filtro["name"] = name
    else:
        return None  

    
    user = collection_users.find_one(
        filtro,
        {
            "_id": 0,
            "name": 1,
            "email": 1,
            "role": 1
        }
    )

    
    if not user:
        return None

   
    return {
        "name": user.get("name"),
        "email": user.get("email"),
        "role": user.get("role")
    }

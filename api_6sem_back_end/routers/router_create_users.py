from fastapi import APIRouter, Depends, HTTPException
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.services.service_create_user import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create")
def create_user(user: dict, payload=Depends(verify_token)):
    try:
        new_user = UserService.create_user(user)
        return {"message": "Usuário criado com sucesso!", "user": new_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
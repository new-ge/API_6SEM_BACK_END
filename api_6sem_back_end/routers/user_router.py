from fastapi import APIRouter, HTTPException
from api_6sem_back_end.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/create")
def create_user(user: dict):
    try:
        new_user = UserService.create_user(user)
        return {"message": "Usuário criado com sucesso!", "user": new_user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
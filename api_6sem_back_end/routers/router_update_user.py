from fastapi import APIRouter, Depends
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.services.service_update_user import UpdateService

router = APIRouter(prefix="/users", tags=["Users"])

@router.put("/edit")
def edit_user(data: dict, payload=Depends(verify_token)):
    return UpdateService.edit_user(data)

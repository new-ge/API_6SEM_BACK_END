from fastapi import APIRouter
from api_6sem_back_end.services.update_service import UpdateService

router = APIRouter(prefix="/users", tags=["Users"])

@router.put("/edit")
def edit_user(data: dict):
    return UpdateService.edit_user(data)

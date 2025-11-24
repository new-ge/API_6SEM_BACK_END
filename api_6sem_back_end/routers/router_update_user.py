from fastapi import APIRouter, Depends
from api_6sem_back_end.repositories.repository_login_security import verify_token
from api_6sem_back_end.services.service_update_user import UpdateService
from api_6sem_back_end.utils.utils_logs import log_action

router = APIRouter(prefix="/users", tags=["Users"])

@router.put("/edit")
@log_action("UPDATE")
def edit_user(data: dict, payload=Depends(verify_token)):
    updated_user = UpdateService.edit_user(data)
    return {
        "message": "Usuário atualizado com sucesso!",
        "user": updated_user["user"]
    }
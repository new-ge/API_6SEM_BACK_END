from fastapi import APIRouter
from pydantic import BaseModel
from api_6sem_back_end.repositories.repository_login_security import create_jwt_token
from api_6sem_back_end.db.de import db_data

router = APIRouter(prefix="/login", tags=["Login"])

class RoleRequest(BaseModel):
    role: str

@router.post("/simulate-login")
def simulate_login(data: RoleRequest):
    role = data.role
    username = f"user_{role.lower()}"
    new_token = create_jwt_token(username, role)
    return {"token": new_token}
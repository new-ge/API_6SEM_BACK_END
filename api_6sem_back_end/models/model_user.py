from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginModel(BaseModel):
    username: Optional[str] = None
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: str
    isActive: bool
    login: LoginModel

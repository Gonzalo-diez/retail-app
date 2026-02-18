from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterIn(BaseModel):
    tenant_name: str
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    tenant_id: int
    email: EmailStr
    role: str
    is_active: bool
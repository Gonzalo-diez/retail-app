from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Literal

Role = Literal["admin", "manager", "cashier"]

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: Role = "cashier"
    is_active: bool = True

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    tenant_id: int

    model_config = ConfigDict(from_attributes=True) 

class UserRoleUpdate(BaseModel):
    role: Role

class UserStatusUpdate(BaseModel):
    is_active: bool
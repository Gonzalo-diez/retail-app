from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class StoreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    timezone: Optional[str] = Field(default=None, max_length=64)
    address: Optional[str] = Field(default=None, max_length=255)

class StoreUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    timezone: Optional[str] = Field(default=None, max_length=64)
    address: Optional[str] = Field(default=None, max_length=255)

class StoreOut(BaseModel):
    id: int
    tenant_id: int
    name: str
    timezone: Optional[str]
    address: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
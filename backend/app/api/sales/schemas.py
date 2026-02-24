from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class SaleIn(BaseModel):
    store_id: int
    sale_date: datetime
    sku: str = Field(min_length=1, max_length=64)
    quantity: float
    unit_price: Optional[float] = None
    revenue: Optional[float] = None
    currency: Optional[str] = "ARS"

class SaleOut(BaseModel):
    id: int
    tenant_id: int
    store_id: int
    sale_date: datetime
    sku: str
    quantity: float
    unit_price: Optional[float]
    revenue: Optional[float]
    currency: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
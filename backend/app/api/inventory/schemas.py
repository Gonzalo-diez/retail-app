from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class InventorySnapshotIn(BaseModel):
    store_id: int
    snapshot_time: datetime
    sku: str = Field(min_length=1, max_length=64)
    stock_qty: float

class InventorySnapshotOut(BaseModel):
    id: int
    tenant_id: int
    store_id: int
    snapshot_time: datetime
    sku: str
    stock_qty: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StockOut(BaseModel):
    sku: str
    snapshot_time: datetime
    stock_qty: float
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any

class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=64)
    name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=255)
    brand: Optional[str] = Field(default=None, max_length=255)
    unit: Optional[str] = Field(default=None, max_length=50)
    barcode: Optional[str] = Field(default=None, max_length=20)

    cost: Optional[float] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    tax_rate: Optional[float] = Field(default=None, ge=0)

    min_stock_qty: Optional[int] = Field(default=None, ge=0)
    max_stock_qty: Optional[int] = Field(default=None, ge=0)
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    pack_size: Optional[int] = Field(default=None, ge=0)

    tags: Optional[Any] = None  # JSONB (lista/dict)
    is_active: bool = True


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(default=None, min_length=1, max_length=64)
    name: Optional[str] = Field(default=None, max_length=255)
    category: Optional[str] = Field(default=None, max_length=255)
    brand: Optional[str] = Field(default=None, max_length=255)
    unit: Optional[str] = Field(default=None, max_length=50)
    barcode: Optional[str] = Field(default=None, max_length=20)

    cost: Optional[float] = Field(default=None, ge=0)
    price: Optional[float] = Field(default=None, ge=0)
    tax_rate: Optional[float] = Field(default=None, ge=0)

    min_stock_qty: Optional[int] = Field(default=None, ge=0)
    max_stock_qty: Optional[int] = Field(default=None, ge=0)
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    pack_size: Optional[int] = Field(default=None, ge=0)

    tags: Optional[Any] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: int
    tenant_id: int
    sku: str
    name: Optional[str]
    category: Optional[str]
    brand: Optional[str]
    unit: Optional[str]
    barcode: Optional[str]
    cost: Optional[float]
    price: Optional[float]
    tax_rate: Optional[float]
    min_stock_qty: Optional[int]
    max_stock_qty: Optional[int]
    lead_time_days: Optional[int]
    pack_size: Optional[int]
    tags: Optional[Any]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
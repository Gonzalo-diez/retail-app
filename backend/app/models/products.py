from sqlalchemy import Column, String, ForeignKey, DateTime, BigInteger, UniqueConstraint, Index, func, Numeric, Integer, Boolean, text
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    sku = Column(String, nullable=False)
    name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    brand = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    barcode = Column(String(20), nullable=True)
    cost = Column(Numeric(10, 2), nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    tax_rate = Column(Numeric(5, 2), nullable=True)
    min_stock_qty = Column(Integer, nullable=True)
    max_stock_qty = Column(Integer, nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    pack_size = Column(Integer, nullable=True)
    tags = Column(JSONB, nullable=True)
    is_active = Column(Boolean, server_default=text("true"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_product_sku_per_tenant"),
        UniqueConstraint("tenant_id", "barcode", name="uq_products_tenant_barcode"),
        Index("ix_products_tenant_id_sku", "tenant_id", "sku"),
        Index("ix_products_tenant_barcode", "tenant_id", "barcode"),
    )
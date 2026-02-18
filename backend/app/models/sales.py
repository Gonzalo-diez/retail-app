from sqlalchemy import Column, Numeric, String, ForeignKey, DateTime, BigInteger, Index, func, text, UniqueConstraint
from app.db.base import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    sale_date = Column(DateTime(timezone=True), nullable=False)
    sku = Column(String, nullable=False)
    quantity = Column(Numeric(14,3), nullable=False)
    unit_price = Column(Numeric(14,2), nullable=True)
    revenue = Column(Numeric(14,2), nullable=True)
    currency = Column(String(3), server_default=text("'ARS'"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "store_id", "sale_date", "sku", name="uq_sales_per_tenant_store_date_sku"),
        Index("ix_sales_tenant_id_store_id_sale_date", "tenant_id", "store_id", "sale_date"),
        Index("ix_sales_tenant_id_sku", "tenant_id", "sku"),
        Index("ix_sales_tenant_id_sale_date", "tenant_id", "sale_date"),
    )
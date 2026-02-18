from sqlalchemy import Column, Numeric, String, BigInteger, DateTime, ForeignKey, Index, func, UniqueConstraint
from app.db.base import Base

class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=False)
    snapshot_time = Column(DateTime(timezone=True), nullable=False)
    sku = Column(String, nullable=False)
    stock_qty = Column(Numeric(14,3), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "store_id", "snapshot_time", "sku", name="uq_inventory_snapshot_per_tenant_store_time_sku"),
        Index("ix_inventory_snapshots_tenant_id_store_id_snapshot_time", "tenant_id", "store_id", "snapshot_time"),
        Index("ix_inventory_snapshots_tenant_id_sku", "tenant_id", "sku"),
    )
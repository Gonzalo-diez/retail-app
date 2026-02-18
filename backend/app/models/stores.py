from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime, Index, func
from app.db.base import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    timezone = Column(String)
    address = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_stores_tenant_id_name", "tenant_id", "name"),
    )
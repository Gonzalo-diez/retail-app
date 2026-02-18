from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Index, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class ColumnMapping(Base):
    __tablename__ = "column_mappings"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    name = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False)
    mapping = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", "dataset_type", name="uq_column_mapping_per_tenant_name_dataset"),
        Index("ix_column_mappings_tenant_id_dataset_type", "tenant_id", "dataset_type"),
    )
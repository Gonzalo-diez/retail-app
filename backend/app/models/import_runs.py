from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Index, func, text
from app.db.base import Base

class ImportRun(Base):
    __tablename__ = "import_runs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=True)
    source_type = Column(String, nullable=False)
    dataset_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    status = Column(String, server_default=text("'uploaded'"), nullable=False)
    rows_total = Column(Integer, server_default=text("0"), nullable=False)
    rows_success = Column(Integer, server_default=text("0"), nullable=False)
    rows_failed = Column(Integer, server_default=text("0"), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_summary = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_import_runs_tenant_id_created_at", "tenant_id", "created_at"),
    )
from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Index, func, Text
from app.db.base import Base

class ImportError(Base):
    __tablename__ = "import_errors"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    import_run_id = Column(BigInteger, ForeignKey("import_runs.id"), nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    row_number = Column(Integer, nullable=False)
    column_name = Column(String, nullable=False)
    error_code = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_import_errors_import_run_id", "import_run_id"),
        Index("ix_import_errors_tenant_id_import_run_id", "tenant_id", "import_run_id"),
    )
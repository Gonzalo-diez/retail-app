from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Index, func, text, Text
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    store_id = Column(BigInteger, ForeignKey("stores.id"), nullable=True)
    type = Column(String, nullable=False)
    severity = Column(String, server_default=text("'medium'"), nullable=False)
    title = Column(String, nullable=False)
    explanation = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=True)
    status = Column(String, server_default=text("'new'"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_recommendations_tenant_id_created_at", "tenant_id", "created_at"),
        Index("ix_recommendations_tenant_id_status", "tenant_id", "status"),
    )
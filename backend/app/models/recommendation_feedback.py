from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, func, Index
from app.db.base import Base

class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    recommendation_id = Column(BigInteger, ForeignKey("recommendations.id"), nullable=False)
    tenant_id = Column(BigInteger, ForeignKey("tenants.id"), nullable=False)
    action = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index("ix_rec_feedback_tenant_id_created_at", "tenant_id", "created_at"),
        Index("ix_rec_feedback_recommendation_id", "recommendation_id"),
    )
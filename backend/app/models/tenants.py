from sqlalchemy import Column, BigInteger, String, DateTime, func
from app.db.base import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    
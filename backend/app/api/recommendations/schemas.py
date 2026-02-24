from datetime import datetime
from fastapi.params import Query
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any, Dict, Literal

RecommendationStatus = Literal["new", "seen", "dismissed", "done"]
RecommendationSeverity = Literal["low", "medium", "high"]

class RecommendationCreate(BaseModel):
    store_id: Optional[int] = None
    type: str = Field(min_length=1, max_length=64)
    severity: RecommendationSeverity = "medium"
    title: str = Field(min_length=1, max_length=255)
    explanation: str = Field(min_length=1)
    payload: Optional[Dict[str, Any]] = None

class RecommendationPatch(BaseModel):
    status: RecommendationStatus | None = Query(default=None)

class RecommendationOut(BaseModel):
    id: int
    tenant_id: int
    store_id: Optional[int]
    type: str
    severity: RecommendationSeverity
    title: str
    explanation: str
    payload: Optional[Dict[str, Any]]
    status: RecommendationStatus | None = Query(default=None)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FeedbackIn(BaseModel):
    action: str = Field(min_length=1, max_length=64)
    notes: Optional[str] = Field(default=None, max_length=255)

class FeedbackOut(BaseModel):
    id: int
    recommendation_id: int
    tenant_id: int
    action: str
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.models.users import User

from .schemas import (
    RecommendationCreate, RecommendationPatch, RecommendationOut,
    FeedbackIn, FeedbackOut
)
from .service import (
    list_recommendations, get_recommendation, create_recommendation,
    update_status, add_feedback, list_feedback
)

recommendation_router = APIRouter()

@recommendation_router.get("/", response_model=list[RecommendationOut])
def recos_list(
    store_id: int | None = Query(default=None),
    status: str | None = Query(default=None),
    type_: str | None = Query(default=None, alias="type"),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_recommendations(
        db,
        tenant_id=current_user.tenant_id,
        store_id=store_id,
        status=status,
        type_=type_,
        limit=limit,
    )

@recommendation_router.post("/", response_model=RecommendationOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def recos_create(
    payload: RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_recommendation(db, tenant_id=current_user.tenant_id, payload=payload.model_dump())

@recommendation_router.patch("/{rec_id}", response_model=RecommendationOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def recos_patch(
    rec_id: int,
    payload: RecommendationPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = get_recommendation(db, tenant_id=current_user.tenant_id, rec_id=rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return update_status(db, rec=rec, status=payload.status)

@recommendation_router.post("/{rec_id}/feedback", response_model=FeedbackOut)
def recos_feedback(
    rec_id: int,
    payload: FeedbackIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = get_recommendation(db, tenant_id=current_user.tenant_id, rec_id=rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return add_feedback(db, tenant_id=current_user.tenant_id, rec_id=rec_id, action=payload.action, notes=payload.notes)

@recommendation_router.get("/{rec_id}/feedback", response_model=list[FeedbackOut])
def recos_feedback_list(
    rec_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rec = get_recommendation(db, tenant_id=current_user.tenant_id, rec_id=rec_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return list_feedback(db, tenant_id=current_user.tenant_id, rec_id=rec_id, limit=limit)
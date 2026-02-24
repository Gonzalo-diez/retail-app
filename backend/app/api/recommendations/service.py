from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.models.recommendation_feedback import RecommendationFeedback
from app.models.stores import Store

ALLOWED_STATUS = {"new", "seen", "dismissed", "done"}

def list_recommendations(db: Session, tenant_id: int, store_id=None, status=None, type_=None, limit: int = 200):
    q = db.query(Recommendation).filter(Recommendation.tenant_id == tenant_id)
    if store_id is not None:
        q = q.filter(Recommendation.store_id == store_id)
    if status:
        q = q.filter(Recommendation.status == status)
    if type_:
        q = q.filter(Recommendation.type == type_)
    return q.order_by(Recommendation.id.desc()).limit(limit).all()

def get_recommendation(db: Session, tenant_id: int, rec_id: int) -> Recommendation | None:
    return db.query(Recommendation).filter(Recommendation.tenant_id == tenant_id, Recommendation.id == rec_id).first()

def create_recommendation(db: Session, tenant_id: int, payload: dict) -> Recommendation:
    store_id = payload.get("store_id")
    if store_id is not None:
        store = db.query(Store).filter(Store.id == store_id, Store.tenant_id == tenant_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="Store not found for this tenant")

    rec = Recommendation(tenant_id=tenant_id, **payload)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def update_status(db: Session, rec: Recommendation, status: str) -> Recommendation:
    if status not in ALLOWED_STATUS:
        raise HTTPException(status_code=422, detail="Invalid status")
    rec.status = status
    db.commit()
    db.refresh(rec)
    return rec

def add_feedback(db: Session, tenant_id: int, rec_id: int, action: str, notes: str | None):
    fb = RecommendationFeedback(tenant_id=tenant_id, recommendation_id=rec_id, action=action, notes=notes)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb

def list_feedback(db: Session, tenant_id: int, rec_id: int, limit: int = 200):
    return (
        db.query(RecommendationFeedback)
        .filter(
            RecommendationFeedback.tenant_id == tenant_id,
            RecommendationFeedback.recommendation_id == rec_id,
        )
        .order_by(RecommendationFeedback.id.desc())
        .limit(limit)
        .all()
    )
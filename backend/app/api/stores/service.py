from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.schemas.page import Page
from app.models.stores import Store
from .schemas import StoreCreate, StoreOut, StoreUpdate

def create_store(db: Session, tenant_id: int, store_in: StoreCreate) -> Store:
    # Evitar duplicados por tenant (soft constraint)
    exists = db.query(Store).filter(Store.tenant_id == tenant_id, Store.name == store_in.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Store name already exists")

    store = Store(tenant_id=tenant_id, **store_in.model_dump())
    db.add(store)
    db.commit()
    db.refresh(store)
    return store

def list_stores(db: Session, *, q: str | None = None, tenant_id: int, page: int, size: int):
    base = db.query(Store).filter(Store.tenant_id == tenant_id)

    if q:
        like = f"%{q.strip()}%"
        base = base.filter(Store.name.ilike(like))

    total = base.with_entities(func.count(Store.id)).scalar() or 0

    items = (
        base.order_by(Store.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    
    items_out = [StoreOut.model_validate(x, from_attributes=True) for x in items]
    return Page[StoreOut].build(items=items_out, page=page, size=size, total=total)

def get_store(db: Session, tenant_id: int, store_id: int) -> Store | None:
    return db.query(Store).filter(Store.tenant_id == tenant_id, Store.id == store_id).first()

def update_store(db: Session, store: Store, store_in: StoreUpdate) -> Store:
    for k, v in store_in.model_dump(exclude_unset=True).items():
        setattr(store, k, v)
    db.commit()
    db.refresh(store)
    return store

def delete_store(db: Session, tenant_id: int, store_id: int) -> None:
    store = get_store(db, tenant_id, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    db.delete(store)
    db.commit()
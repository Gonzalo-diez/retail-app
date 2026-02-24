from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.stores import Store
from .schemas import StoreCreate, StoreUpdate

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

def list_stores(db: Session, tenant_id: int):
    return (
        db.query(Store)
        .filter(Store.tenant_id == tenant_id)
        .order_by(Store.id.desc())
        .all()
    )

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
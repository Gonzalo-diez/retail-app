from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.schemas.page import Page
from app.models.users import User
from .schemas import StoreCreate, StoreUpdate, StoreOut
from .service import create_store, list_stores, get_store, update_store, delete_store

store_router = APIRouter()

@store_router.get("/", response_model=Page[StoreOut])
def stores_list(
    q: str | None = Query(default=None, description="Search: store name/address"),
    db: Session = Depends(get_db),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    return list_stores(db, q=q, page=page, size=size, tenant_id=current_user.tenant_id)

@store_router.get("/{store_id}", response_model=StoreOut)
def stores_get(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = get_store(db, tenant_id=current_user.tenant_id, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@store_router.post("/", response_model=StoreOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def stores_create(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_store(db, tenant_id=current_user.tenant_id, store_in=payload)

@store_router.patch("/{store_id}", response_model=StoreOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def stores_update(
    store_id: int,
    payload: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = get_store(db, tenant_id=current_user.tenant_id, store_id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return update_store(db, store=store, store_in=payload)

@store_router.delete("/{store_id}", status_code=204, dependencies=[Depends(require_roles(["admin", "manager"]))])
def stores_delete(
    store_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_store(db, tenant_id=current_user.tenant_id, store_id=store_id)
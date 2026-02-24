from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_user, require_roles
from app.models.users import User
from .schemas import SaleIn, SaleOut
from .service import bulk_upsert_sales, list_sales

sales_router = APIRouter()

@sales_router.post("/bulk", response_model=dict, dependencies=[Depends(require_roles(["admin", "manager"]))])
def sales_bulk(
    payload: list[SaleIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = [p.model_dump() for p in payload]
    n = bulk_upsert_sales(db, tenant_id=current_user.tenant_id, rows=rows)
    return {"upserted": n}

@sales_router.get("/", response_model=list[SaleOut])
def sales_list(
    store_id: int | None = Query(default=None),
    sku: str | None = Query(default=None),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_sales(db, tenant_id=current_user.tenant_id, store_id=store_id, sku=sku, date_from=date_from, date_to=date_to, limit=limit)
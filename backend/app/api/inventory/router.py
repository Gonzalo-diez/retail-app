from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.models.users import User
from .schemas import InventorySnapshotIn, InventorySnapshotOut, StockOut
from .service import bulk_upsert_snapshots, get_current_stock

inventory_router = APIRouter()

@inventory_router.post("/snapshots/bulk", response_model=dict, dependencies=[Depends(require_roles(["admin", "manager"]))])
def snapshots_bulk(
    payload: list[InventorySnapshotIn],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = [p.model_dump() for p in payload]
    n = bulk_upsert_snapshots(db, tenant_id=current_user.tenant_id, rows=rows)
    return {"upserted": n}

@inventory_router.get("/stock", response_model=list[StockOut])
def stock_current(
    store_id: int = Query(...),
    limit: int = Query(default=500, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_current_stock(db, tenant_id=current_user.tenant_id, store_id=store_id, limit=limit)
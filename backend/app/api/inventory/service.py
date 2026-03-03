from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, and_
from app.models.inventory_snapshots import InventorySnapshot
from app.models.stores import Store

def bulk_upsert_snapshots(db: Session, tenant_id: int, rows: list[dict]) -> int:
    if not rows:
        return 0
    
    store_ids = {r["store_id"] for r in rows if r.get("store_id") is not None}
    if store_ids:
        ok = (
            db.query(Store.id)
            .filter(Store.tenant_id == tenant_id, Store.id.in_(store_ids))
            .all()
        )
        ok_ids = {x[0] for x in ok}
        missing = store_ids - ok_ids
        if missing:
            raise HTTPException(status_code=404, detail=f"Store not found: {sorted(missing)}")
    
    for r in rows:
        r["tenant_id"] = tenant_id

    stmt = insert(InventorySnapshot).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_inventory_snapshot_per_tenant_store_time_sku",
        set_={"stock_qty": stmt.excluded.stock_qty},
    )
    db.execute(stmt)
    db.commit()
    return len(rows)

def get_current_stock(db: Session, tenant_id: int, store_id: int, limit: int = 500):
    store = db.query(Store).filter(Store.id == store_id, Store.tenant_id == tenant_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    
    sub = (
        db.query(
            InventorySnapshot.sku.label("sku"),
            func.max(InventorySnapshot.snapshot_time).label("mx"),
        )
        .filter(InventorySnapshot.tenant_id == tenant_id, InventorySnapshot.store_id == store_id)
        .group_by(InventorySnapshot.sku)
        .subquery()
    )

    q = (
        db.query(InventorySnapshot.sku, InventorySnapshot.snapshot_time, InventorySnapshot.stock_qty)
        .join(sub, and_(InventorySnapshot.sku == sub.c.sku, InventorySnapshot.snapshot_time == sub.c.mx))
        .filter(InventorySnapshot.tenant_id == tenant_id, InventorySnapshot.store_id == store_id)
        .order_by(InventorySnapshot.sku.asc())
        .limit(limit)
        .all()
    )
    return [{"sku": r[0], "snapshot_time": r[1], "stock_qty": float(r[2])} for r in q]
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import func, and_
from app.models.inventory_snapshots import InventorySnapshot

def bulk_upsert_snapshots(db: Session, tenant_id: int, rows: list[dict]) -> int:
    if not rows:
        return 0
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
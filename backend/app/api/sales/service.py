from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.models.sales import Sale

def bulk_upsert_sales(db: Session, tenant_id: int, rows: list[dict]) -> int:
    if not rows:
        return 0
    for r in rows:
        r["tenant_id"] = tenant_id

    stmt = insert(Sale).values(rows)
    stmt = stmt.on_conflict_do_update(
        constraint="uq_sales_per_tenant_store_date_sku",
        set_={
            "quantity": stmt.excluded.quantity,
            "unit_price": stmt.excluded.unit_price,
            "revenue": stmt.excluded.revenue,
            "currency": stmt.excluded.currency,
        },
    )
    db.execute(stmt)
    db.commit()
    return len(rows)

def list_sales(db: Session, tenant_id: int, store_id: int | None = None, sku: str | None = None, date_from=None, date_to=None, limit: int = 200):
    q = db.query(Sale).filter(Sale.tenant_id == tenant_id)
    if store_id:
        q = q.filter(Sale.store_id == store_id)
    if sku:
        q = q.filter(Sale.sku == sku)
    if date_from:
        q = q.filter(Sale.sale_date >= date_from)
    if date_to:
        q = q.filter(Sale.sale_date <= date_to)
    return q.order_by(Sale.sale_date.desc()).limit(limit).all()
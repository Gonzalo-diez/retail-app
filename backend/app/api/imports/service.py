from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.schemas.page import Page
from app.api.imports.schemas import ImportRunOut
from app.models.import_runs import ImportRun
from app.models.import_errors import ImportError
from app.models.column_mappings import ColumnMapping

ALLOWED_DATASETS = {"products", "sales", "inventory"}

ALLOWED_FIELDS = {
    "products": {"sku", "name", "brand", "category", "barcode", "price", "cost"},
    "sales": {"sku", "sale_date", "quantity", "unit_price", "revenue"},
    "inventory": {"sku", "snapshot_time", "stock_qty"},
}

def list_runs(db: Session, *, q: str | None = None, tenant_id: int, page: int, size: int):
    base = db.query(ImportRun).filter(ImportRun.tenant_id == tenant_id)

    if q:
        like = f"%{q.strip()}%"
        base = base.filter(ImportRun.original_filename.ilike(like))

    total = base.with_entities(func.count(ImportRun.id)).scalar() or 0

    items = (
        base.order_by(ImportRun.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items_out = [ImportRunOut.model_validate(x, from_attributes=True) for x in items]
    return Page[ImportRunOut].build(items=items_out, page=page, size=size, total=total)

def get_run(db: Session, tenant_id: int, run_id: int) -> ImportRun | None:
    return db.query(ImportRun).filter(ImportRun.tenant_id == tenant_id, ImportRun.id == run_id).first()

def list_errors(db: Session, tenant_id: int, run_id: int, limit: int = 200):
    return (
        db.query(ImportError)
        .filter(ImportError.tenant_id == tenant_id, ImportError.import_run_id == run_id)
        .order_by(ImportError.id.asc())
        .limit(limit)
        .all()
    )

def create_run(
    db: Session,
    tenant_id: int,
    user_id: int,
    dataset_type: str,
    source_type: str,
    original_filename: str,
    file_path: str,
    store_id: int | None = None,
) -> ImportRun:
    run = ImportRun(
        tenant_id=tenant_id,
        user_id=user_id,
        store_id=store_id,
        dataset_type=dataset_type,
        source_type=source_type,
        original_filename=original_filename,
        file_path=file_path,
        status="uploaded",
        rows_total=0,
        rows_success=0,
        rows_failed=0,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def update_run_file_path(db: Session, run: ImportRun, file_path: str) -> ImportRun:
    run.file_path = file_path
    db.commit()
    db.refresh(run)
    return run

def create_mapping(db: Session, tenant_id: int, name: str, dataset_type: str, mapping: dict) -> ColumnMapping:
    if dataset_type not in ALLOWED_DATASETS:
        raise HTTPException(status_code=422, detail="Invalid dataset_type")

    bad = [v for v in mapping.values() if v not in ALLOWED_FIELDS[dataset_type]]
    if bad:
        raise HTTPException(status_code=422, detail=f"Invalid target fields in mapping: {sorted(set(bad))}")
    
    cm = ColumnMapping(tenant_id=tenant_id, name=name, dataset_type=dataset_type, mapping=mapping)
    try:
        db.add(cm)
        db.commit()
        db.refresh(cm)
        return cm
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Mapping name already exists for this dataset_type")

def list_mappings(db: Session, tenant_id: int, dataset_type: str | None = None):
    q = db.query(ColumnMapping).filter(ColumnMapping.tenant_id == tenant_id)
    if dataset_type:
        q = q.filter(ColumnMapping.dataset_type == dataset_type)
    return q.order_by(ColumnMapping.id.desc()).all()
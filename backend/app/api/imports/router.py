import os
from typing import Optional
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.stores import Store
from app.schemas.page import Page
from app.api.deps import get_db, get_current_user, require_roles
from app.models.users import User
from app.tasks.queue import get_queue
from app.tasks.import_jobs import process_import_run

from .schemas import DatasetType, ImportRunOut, ImportErrorOut, ColumnMappingCreate, ColumnMappingOut, ProcessOut
from .service import (
    create_run, update_run_file_path, list_runs, get_run, list_errors,
    create_mapping, list_mappings
)

import_router = APIRouter()

UPLOAD_ROOT = "uploads"

def _safe_name(name: str) -> str:
    return Path(name).name.replace("\\", "_").replace("/", "_")

@import_router.get("/runs", response_model=Page[ImportRunOut])
def runs_list(
    q: str | None = Query(default=None, description="Search: original filename"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_runs(db, q=q, page=page, size=size, tenant_id=current_user.tenant_id)

@import_router.get("/runs/{run_id}", response_model=ImportRunOut)
def runs_get(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = get_run(db, tenant_id=current_user.tenant_id, run_id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="ImportRun not found")
    return run

@import_router.get("/runs/{run_id}/errors", response_model=list[ImportErrorOut])
def runs_errors(
    run_id: int,
    limit: int = Query(default=200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = get_run(db, tenant_id=current_user.tenant_id, run_id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="ImportRun not found")
    return list_errors(db, tenant_id=current_user.tenant_id, run_id=run_id, limit=limit)

@import_router.post("/upload", response_model=ImportRunOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def upload(
    dataset_type: str = Form(...),
    store_id: int | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if store_id is not None:
        store = (
            db.query(Store)
            .filter(Store.id == store_id, Store.tenant_id == current_user.tenant_id)
            .first()
        )
        if not store:
            raise HTTPException(status_code=404, detail="Store not found")
    
    original = _safe_name(file.filename or "file")
    # crear run con file_path temporal
    run = create_run(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        dataset_type=dataset_type,
        source_type="excel",
        original_filename=original,
        file_path="pending",
        store_id=store_id,
    )

    # guardar archivo
    tenant_dir = os.path.join(UPLOAD_ROOT, f"tenant_{current_user.tenant_id}", f"run_{run.id}")
    os.makedirs(tenant_dir, exist_ok=True)
    dst = os.path.join(tenant_dir, original)

    with open(dst, "wb") as out:
        out.write(file.file.read())

    run = update_run_file_path(db, run, file_path=dst)

    # encolar procesamiento
    q = get_queue()
    q.enqueue(process_import_run, run.id)

    return run

@import_router.post("/runs/{run_id}/process", response_model=ProcessOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def process(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    run = get_run(db, tenant_id=current_user.tenant_id, run_id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="ImportRun not found")

    q = get_queue()
    q.enqueue(process_import_run, run.id)
    return {"import_run_id": run.id, "enqueued": True}

@import_router.post("/mappings", response_model=ColumnMappingOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def mappings_create(
    payload: ColumnMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_mapping(db, tenant_id=current_user.tenant_id, name=payload.name, dataset_type=payload.dataset_type, mapping=payload.mapping)

@import_router.get("/mappings", response_model=list[ColumnMappingOut])
def mappings_list(
    dataset_type: Optional[DatasetType] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_mappings(db, tenant_id=current_user.tenant_id, dataset_type=dataset_type)
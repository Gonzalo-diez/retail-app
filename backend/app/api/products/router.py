from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.models.users import User
from .schemas import ProductCreate, ProductUpdate, ProductOut
from .service import create_product, list_products, get_product, update_product, delete_product

product_router = APIRouter()

@product_router.get("/", response_model=list[ProductOut])
def products_list(
    q: str | None = Query(default=None, description="Search: sku/name/barcode/brand/category"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_products(db, tenant_id=current_user.tenant_id, q=q, page=page, size=size)


@product_router.get("/{product_id}", response_model=ProductOut)
def products_get(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = get_product(db, tenant_id=current_user.tenant_id, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@product_router.post("/", response_model=ProductOut, dependencies=[Depends(require_roles(["admin", "manager"]))])
def products_create(
    payload: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_product(db, tenant_id=current_user.tenant_id, product_in=payload)


@product_router.patch("/{product_id}", response_model=ProductOut)
def products_update(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = get_product(db, product_id=product_id, tenant_id=current_user.tenant_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return update_product(db, product=product, product_in=payload)


@product_router.delete("/{product_id}", status_code=204, dependencies=[Depends(require_roles(["admin", "manager"]))])
def products_delete(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_product(db, tenant_id=current_user.tenant_id, product_id=product_id)
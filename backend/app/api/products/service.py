from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.products import Product
from app.api.products.schemas import ProductCreate, ProductUpdate


def create_product(db: Session, product_in: ProductCreate, tenant_id: int) -> Product:
    product = Product(
        tenant_id=tenant_id,
        **product_in.model_dump()
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    except IntegrityError as e:
        db.rollback()

        # Mensaje real del motor
        detail = str(e.orig)

        if "uq_product_sku_per_tenant" in detail:
            raise HTTPException(status_code=400, detail="SKU already exists for this tenant")

        if "uq_products_tenant_barcode" in detail:
            raise HTTPException(status_code=400, detail="Barcode already exists for this tenant")

        raise HTTPException(status_code=400, detail=detail)


def get_product(db: Session, product_id: int, tenant_id: int) -> Product | None:
    return db.query(Product).filter(
        Product.id == product_id,
        Product.tenant_id == tenant_id
    ).first()


def list_products(db, tenant_id: int, q: str | None = None, page: int = 1, size: int = 50):
    query = db.query(Product).filter(Product.tenant_id == tenant_id)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Product.sku.ilike(like),
                Product.name.ilike(like),
                Product.barcode.ilike(like),
                Product.brand.ilike(like),
                Product.category.ilike(like),
            )
        )

    return (
        query
        .order_by(Product.id.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )


def update_product(
    db: Session,
    product: Product,
    product_in: ProductUpdate
) -> Product:

    for field, value in product_in.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)
        return product

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e.orig))


def delete_product(db: Session, tenant_id: int, product_id: int):
    product = get_product(db, product_id=product_id, tenant_id=tenant_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
import os
from datetime import datetime, timezone
from decimal import Decimal
import pandas as pd
from sqlalchemy.dialects.postgresql import insert

from app.db.session import SessionLocal
from app.models.import_runs import ImportRun
from app.models.import_errors import ImportError
from app.models.products import Product
from app.models.sales import Sale
from app.models.inventory_snapshots import InventorySnapshot

ALLOWED_DATASETS = {"products", "sales", "inventory"}

def _now():
    return datetime.now(timezone.utc)

def _safe_num(x):
    if x is None or (isinstance(x, float) and pd.isna(x)) or (isinstance(x, str) and not x.strip()):
        return None
    try:
        return Decimal(str(x))
    except Exception:
        return None

def _find_col(cols, candidates):
    cols_norm = {c.strip().lower(): c for c in cols}
    for cand in candidates:
        if cand in cols_norm:
            return cols_norm[cand]
    return None

def process_import_run(import_run_id: int) -> None:
    db = SessionLocal()
    run = None

    def fail(msg: str):
        nonlocal run
        if run:
            run.status = "failed"
            run.error_summary = msg[:255]
            run.finished_at = _now()
            db.commit()

    try:
        run = db.get(ImportRun, import_run_id)
        if not run:
            return

        # Marcar inicio SIEMPRE
        run.status = "processing"
        run.started_at = _now()
        db.commit()

        if run.dataset_type not in ALLOWED_DATASETS:
            fail(f"Unsupported dataset_type: {run.dataset_type}")
            return

        path = run.file_path
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)

        if not os.path.exists(path):
            fail(f"File not found: {path}")
            return

        # Leer archivo
        if path.lower().endswith(".csv"):
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path, engine="openpyxl")

        df.columns = [str(c) for c in df.columns]
        total = int(len(df.index))

        if total == 0:
            fail("Empty file: no rows found")
            return

        errors: list[ImportError] = []
        rows: list[dict] = []

        # Para un conteo "real" de upsert
        affected_rows = 0

        # ---------------------------
        # PRODUCTS
        # ---------------------------
        if run.dataset_type == "products":
            sku_col = _find_col(df.columns, ["sku", "código", "codigo", "code"])
            name_col = _find_col(df.columns, ["name", "nombre"])
            brand_col = _find_col(df.columns, ["brand", "marca"])
            category_col = _find_col(df.columns, ["category", "categoria", "categoría"])
            barcode_col = _find_col(df.columns, ["barcode", "ean", "codigobarra", "código de barras", "codigo de barras"])
            price_col = _find_col(df.columns, ["price", "precio"])
            cost_col = _find_col(df.columns, ["cost", "costo"])

            if not sku_col:
                fail("Missing SKU column")
                return

            for i, r in df.iterrows():
                rownum = int(i) + 2
                sku = str(r.get(sku_col) or "").strip()
                if not sku:
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=sku_col,
                        error_code="missing_required", message="SKU is required"
                    ))
                    continue

                rows.append({
                    "tenant_id": run.tenant_id,
                    "sku": sku,
                    "name": (str(r.get(name_col)).strip() if name_col and r.get(name_col) is not None else None),
                    "brand": (str(r.get(brand_col)).strip() if brand_col and r.get(brand_col) is not None else None),
                    "category": (str(r.get(category_col)).strip() if category_col and r.get(category_col) is not None else None),
                    "barcode": (str(r.get(barcode_col)).strip() if barcode_col and r.get(barcode_col) is not None else None),
                    "price": _safe_num(r.get(price_col)) if price_col else None,
                    "cost": _safe_num(r.get(cost_col)) if cost_col else None,
                })

            if rows:
                stmt = insert(Product).values(rows)
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_product_sku_per_tenant",
                    set_={
                        "name": stmt.excluded.name,
                        "brand": stmt.excluded.brand,
                        "category": stmt.excluded.category,
                        "barcode": stmt.excluded.barcode,
                        "price": stmt.excluded.price,
                        "cost": stmt.excluded.cost,
                    },
                ).returning(Product.id)

                result = db.execute(stmt)
                affected_rows = len(result.fetchall())
                db.commit()

        # ---------------------------
        # SALES
        # ---------------------------
        elif run.dataset_type == "sales":
            if not run.store_id:
                fail("store_id is required for sales imports")
                return

            sku_col = _find_col(df.columns, ["sku", "código", "codigo", "code"])
            date_col = _find_col(df.columns, ["sale_date", "fecha", "date"])
            qty_col = _find_col(df.columns, ["quantity", "qty", "cantidad"])
            price_col = _find_col(df.columns, ["unit_price", "precio_unitario", "precio unitario", "price"])
            revenue_col = _find_col(df.columns, ["revenue", "importe", "total", "venta"])

            if not sku_col or not date_col or not qty_col:
                fail("Missing required columns for sales (sku, date, quantity)")
                return

            for i, r in df.iterrows():
                rownum = int(i) + 2
                sku = str(r.get(sku_col) or "").strip()
                if not sku:
                    # FIX: crear ImportError con kwargs correctos (tu código tenía una firma mala)
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=sku_col,
                        error_code="missing_required", message="SKU is required"
                    ))
                    continue

                dt = pd.to_datetime(r.get(date_col), errors="coerce", utc=True)
                if pd.isna(dt):
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=date_col,
                        error_code="invalid_date", message="Invalid sale_date"
                    ))
                    continue

                qty = _safe_num(r.get(qty_col))
                if qty is None:
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=qty_col,
                        error_code="invalid_number", message="Invalid quantity"
                    ))
                    continue

                rows.append({
                    "tenant_id": run.tenant_id,
                    "store_id": run.store_id,
                    "sale_date": dt.to_pydatetime(),
                    "sku": sku,
                    "quantity": qty,
                    "unit_price": _safe_num(r.get(price_col)) if price_col else None,
                    "revenue": _safe_num(r.get(revenue_col)) if revenue_col else None,
                    "currency": "ARS",
                })

            if rows:
                stmt = insert(Sale).values(rows)
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_sales_per_tenant_store_date_sku",
                    set_={
                        "quantity": stmt.excluded.quantity,
                        "unit_price": stmt.excluded.unit_price,
                        "revenue": stmt.excluded.revenue,
                        "currency": stmt.excluded.currency,
                    },
                ).returning(Sale.id)

                result = db.execute(stmt)
                affected_rows = len(result.fetchall())
                db.commit()

        # ---------------------------
        # INVENTORY
        # ---------------------------
        else:
            if not run.store_id:
                fail("store_id is required for inventory imports")
                return

            sku_col = _find_col(df.columns, ["sku", "código", "codigo", "code"])
            time_col = _find_col(df.columns, ["snapshot_time", "fecha", "date", "time"])
            stock_col = _find_col(df.columns, ["stock_qty", "stock", "existencia", "cantidad"])

            if not sku_col or not time_col or not stock_col:
                fail("Missing required columns for inventory (sku, time, stock_qty)")
                return

            for i, r in df.iterrows():
                rownum = int(i) + 2
                sku = str(r.get(sku_col) or "").strip()
                if not sku:
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=sku_col,
                        error_code="missing_required", message="SKU is required"
                    ))
                    continue

                dt = pd.to_datetime(r.get(time_col), errors="coerce", utc=True)
                if pd.isna(dt):
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=time_col,
                        error_code="invalid_date", message="Invalid snapshot_time"
                    ))
                    continue

                stock = _safe_num(r.get(stock_col))
                if stock is None:
                    errors.append(ImportError(
                        import_run_id=run.id, tenant_id=run.tenant_id,
                        row_number=rownum, column_name=stock_col,
                        error_code="invalid_number", message="Invalid stock_qty"
                    ))
                    continue

                rows.append({
                    "tenant_id": run.tenant_id,
                    "store_id": run.store_id,
                    "snapshot_time": dt.to_pydatetime(),
                    "sku": sku,
                    "stock_qty": stock,
                })

            if rows:
                stmt = insert(InventorySnapshot).values(rows)
                stmt = stmt.on_conflict_do_update(
                    constraint="uq_inventory_snapshot_per_tenant_store_time_sku",
                    set_={"stock_qty": stmt.excluded.stock_qty},
                ).returning(InventorySnapshot.id)

                result = db.execute(stmt)
                affected_rows = len(result.fetchall())
                db.commit()

        # Guardar errores (si los hay)
        if errors:
            db.add_all(errors)
            db.commit()

        # CONTEOS CORRECTOS:
        # total: filas leídas del excel
        # failed: filas skippeadas por validación
        # success: filas válidas intentadas
        valid = len(rows)
        failed_count = len(errors)

        run.rows_total = total
        run.rows_failed = failed_count

        # Si pudimos contar affected_rows (RETURNING), lo uso; si no, caigo a "valid"
        run.rows_success = affected_rows if rows else 0
        if run.rows_success == 0 and valid > 0:
            # fallback si por alguna razón RETURNING no devolvió filas
            run.rows_success = valid

        run.status = "done" if run.rows_success > 0 else "failed"
        run.finished_at = _now()
        db.commit()

    except Exception as e:
        # Marcar fallo en DB y volver a lanzar para que RQ lo marque como failed si querés
        try:
            if run is None:
                run = db.get(ImportRun, import_run_id)
            if run:
                run.status = "failed"
                run.error_summary = str(e)[:255]
                run.finished_at = _now()
                db.commit()
        finally:
            pass
        raise
    finally:
        db.close()
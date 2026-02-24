from fastapi import APIRouter

from app.api.auth.router import auth_router
from app.api.users.router import user_router
from app.api.products.router import product_router
from app.api.stores.router import store_router
from app.api.imports.router import import_router
from app.api.sales.router import sales_router
from app.api.inventory.router import inventory_router
from app.api.recommendations.router import recommendation_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(product_router, prefix="/products", tags=["products"])
api_router.include_router(store_router, prefix="/stores", tags=["stores"])
api_router.include_router(import_router, prefix="/imports", tags=["imports"])
api_router.include_router(sales_router, prefix="/sales", tags=["sales"])
api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
api_router.include_router(recommendation_router, prefix="/recommendations", tags=["recommendations"])
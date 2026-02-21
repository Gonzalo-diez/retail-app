from fastapi import APIRouter

from app.api.auth.router import auth_router
from app.api.users.router import user_router
from app.api.products.router import product_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router, prefix="/users", tags=["users"])
api_router.include_router(product_router, prefix="/products", tags=["products"])
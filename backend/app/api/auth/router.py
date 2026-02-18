from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.api.auth.schemas import RegisterIn, LoginIn, TokenOut, UserOut
from app.api.auth.service import register_tenant_and_admin, login

auth_router = APIRouter()

@auth_router.post("/register", response_model=TokenOut)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    token = register_tenant_and_admin(db, payload.tenant_name, payload.email, payload.password)
    return {"access_token": token}

@auth_router.post("/login", response_model=TokenOut)
def do_login(payload: LoginIn, db: Session = Depends(get_db)):
    token = login(db, payload.email, payload.password)
    return {"access_token": token}

@auth_router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user
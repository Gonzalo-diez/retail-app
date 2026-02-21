from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user, require_roles
from app.models.users import User

from .schemas import UserCreate, UserOut, UserRoleUpdate, UserStatusUpdate
from .service import create_user, list_users, update_user_role, update_user_status

user_router = APIRouter()

@user_router.get("/", response_model=list[UserOut], dependencies=[Depends(require_roles(["admin"]))])
def users_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_users(db, tenant_id=current_user.tenant_id)

@user_router.post("/", response_model=UserOut, dependencies=[Depends(require_roles(["admin"]))])
def users_create(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # tenant_id SIEMPRE sale del token
    return create_user(
        db,
        tenant_id=current_user.tenant_id,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )

@user_router.patch("/{user_id}/role", response_model=UserOut, dependencies=[Depends(require_roles(["admin"]))])
def users_update_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_role(db, tenant_id=current_user.tenant_id, user_id=user_id, role=payload.role)

@user_router.patch("/{user_id}/status", response_model=UserOut, dependencies=[Depends(require_roles(["admin"]))])
def users_update_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user_status(db, tenant_id=current_user.tenant_id, user_id=user_id, is_active=payload.is_active)

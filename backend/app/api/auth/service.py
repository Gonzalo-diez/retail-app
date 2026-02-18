from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.tenants import Tenant
from app.models.users import User
from app.api.auth.security import hash_password, verify_password, create_access_token

def register_tenant_and_admin(db: Session, tenant_name: str, email: str, password: str) -> str:
    # Chequeo simple: si el email existe en algún tenant, lo permitís igual (depende tu política)
    # Para MVP lo dejamos simple: prohibimos duplicado dentro del mismo tenant, pero acá aún no existe.
    tenant = Tenant(name=tenant_name)
    db.add(tenant)
    db.flush()  # para tener tenant.id

    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return create_access_token(sub=str(user.id), tenant_id=user.tenant_id, role=user.role)

def login(db: Session, email: str, password: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return create_access_token(sub=str(user.id), tenant_id=user.tenant_id, role=user.role)
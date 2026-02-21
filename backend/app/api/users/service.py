from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.users import User
from app.core.security import hash_password

def create_user(db: Session, *, tenant_id: int, email: str, password: str, role: str, is_active: bool) -> User:
    existing = db.query(User).filter(User.tenant_id == tenant_id, User.email == email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists in this tenant")

    user = User(
        tenant_id=tenant_id,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def list_users(db: Session, *, tenant_id: int) -> list[User]:
    return (
        db.query(User)
        .filter(User.tenant_id == tenant_id)
        .order_by(User.id.desc())
        .all()
    )

def get_user_in_tenant(db: Session, *, tenant_id: int, user_id: int) -> User:
    user = db.query(User).filter(User.tenant_id == tenant_id, User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def update_user_role(db: Session, *, tenant_id: int, user_id: int, role: str) -> User:
    user = get_user_in_tenant(db, tenant_id=tenant_id, user_id=user_id)
    user.role = role
    db.commit()
    db.refresh(user)
    return user

def update_user_status(db: Session, *, tenant_id: int, user_id: int, is_active: bool) -> User:
    user = get_user_in_tenant(db, tenant_id=tenant_id, user_id=user_id)
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user

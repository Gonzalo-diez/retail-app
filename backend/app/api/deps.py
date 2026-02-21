from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from typing import Iterable, Callable

from app.core.security import JWT_ALG, JWT_SECRET
from app.models.users import User
from app.db.deps import get_db


bearer_scheme = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = creds.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
        token_tenant_id = payload.get("tenant_id")

        if not user_id or token_tenant_id is None:
            raise ValueError("missing claims")

    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.get(User, int(user_id))

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or missing user")

    if int(user.tenant_id) != int(token_tenant_id):
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

def require_roles(allowed: Iterable[str]) -> Callable:
    allowed_set = set(allowed)

    def _dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

    return _dep
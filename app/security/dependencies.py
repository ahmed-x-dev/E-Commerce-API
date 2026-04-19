# app/security/dependencies.py
from __future__ import annotations
from typing import TYPE_CHECKING

from app.db.schemas.user_schema import UserRole

if TYPE_CHECKING:
    from app.db.models.user_model import User

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.security.jwt import decode_token
from app.db.session import get_db
from app.services.user_service import user_service


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 1. Decode returns a string (e.g., "3")
        user_id_raw = decode_token(token, expected_type="access")
        
        # 2. Cast to int to satisfy Postgres
        user_id = int(user_id_raw) 
        
    except (JWTError, ValueError, TypeError):
        # ValueError/TypeError catches cases where user_id isn't a number
        raise credentials_exception

    user = user_service.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user




def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user





def require_role(*roles: str):
    """Factory that returns a dependency requiring specific roles."""
    async def checker(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return checker

# Shorthand dependencies
get_admin_user = require_role(UserRole.admin)
get_staff_user = require_role(UserRole.admin, UserRole.staff)
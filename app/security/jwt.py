# app/security/jwt.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode({"sub": subject, "exp": expire, "type": "access"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return jwt.encode({"sub": subject, "exp": expire, "type": "refresh"}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: str = "access") -> str:
    """Returns the subject (user_id) or raises JWTError."""
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    if payload.get("type") != expected_type:
        raise JWTError(f"Invalid token type: expected '{expected_type}'")

    subject = payload.get("sub")
    if subject is None:
        raise JWTError("Missing subject")

    return subject
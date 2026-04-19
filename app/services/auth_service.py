# app/services/user_services.py
from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils.email import send_email
from app.security.hashing import hash_password, verify_password

from app.db.models.token_model import RefreshToken
from app.db.models.user_model import User
from app.db.models.verification_model import EmailVerification, PasswordReset



from app.db.schemas.auth_schema import LoginRequest,EmailVerificationRequest
from app.db.schemas.user_schema import UserCreate, UserRead

from app.security.jwt import create_access_token, create_refresh_token, decode_token


class AuthService:

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _generate_code() -> tuple[str, str]:
        """Returns (plain_code, hashed_code)."""
        code = str(random.randint(100000, 999999))
        hashed = hashlib.sha256(code.encode()).hexdigest()
        return code, hashed

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    # -------------------------------------------------------------------------
    # Register
    # -------------------------------------------------------------------------

    @staticmethod
    def register(db: Session, data: UserCreate) -> UserRead:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        db.flush()  # get user.id without committing yet

        code, hashed = AuthService._generate_code() # generate verification code and hash
        db.add(EmailVerification(
            user_id=user.id,
            code_hash=hashed,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        ))
        db.commit()
        db.refresh(user)

        send_email(
            to=user.email,
            subject="Verify your email",
            body=f"Your verification code is: {code}\nExpires in 15 minutes.",
        )

        return UserRead.model_validate(user)

    # -------------------------------------------------------------------------
    # Verify email
    # -------------------------------------------------------------------------

    @staticmethod
    def verify_email(db: Session, data: EmailVerificationRequest) -> None:
        user = db.query(User).filter(User.email == data.email, User.is_deleted == False).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

        hashed = hashlib.sha256(data.code.encode()).hexdigest()
        verification = (
            db.query(EmailVerification)
            .filter(
                EmailVerification.user_id == user.id,
                EmailVerification.code_hash == hashed,
                EmailVerification.used == False,
            )
            .first()
        )

        if not verification:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code")
        if verification.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code expired")

        verification.used = True
        user.is_verified = True
        db.commit()

    # -------------------------------------------------------------------------
    # Login
    # -------------------------------------------------------------------------

    @staticmethod
    def login(db: Session, data: LoginRequest) -> tuple[str, str]:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
        user = db.query(User).filter(User.email == data.email, User.is_deleted == False).first()

        if not user or not verify_password(data.password, user.password_hash):
            raise credentials_exception
        if not user.is_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email not verified")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account inactive")

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        db.add(RefreshToken(
            user_id=user.id,
            token_hash=AuthService._hash_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        ))
        db.commit()


        return access_token, refresh_token

    # -------------------------------------------------------------------------
    # Refresh
    # -------------------------------------------------------------------------

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> tuple[str, str]:
        try:
            user_id = decode_token(refresh_token, expected_type="refresh")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        stored = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == AuthService._hash_token(refresh_token),
                RefreshToken.revoked == False,
            )
            .first()
        )

        if not stored or stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

        # Rotate: revoke old, issue new
        stored.revoked = True

        new_access = create_access_token(subject=user_id)
        new_refresh = create_refresh_token(subject=user_id)

        db.add(RefreshToken(
            user_id=stored.user_id,
            token_hash=AuthService._hash_token(new_refresh),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        ))
        db.commit()

        return new_access, new_refresh

    # -------------------------------------------------------------------------
    # Logout
    # -------------------------------------------------------------------------

    @staticmethod
    def logout(db: Session, refresh_token: str) -> None:
        db.query(RefreshToken).filter(
            RefreshToken.token_hash == AuthService._hash_token(refresh_token)
        ).update({"revoked": True})
        db.commit()


    # -------------------------------------------------------------------------
    # Forgot password
    # -------------------------------------------------------------------------

    @staticmethod
    def forgot_password(db: Session, email: EmailStr) -> None:
        user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
        if not user:
            return  # silent — avoids email enumeration

        code, hashed = AuthService._generate_code()
        db.add(PasswordReset(
            user_id=user.id,
            code_hash=hashed,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
        ))
        db.commit()

        send_email(
            to=user.email,
            subject="Reset your password",
            body=f"Your password reset code is: {code}\nExpires in 15 minutes.",
        )

    # -------------------------------------------------------------------------
    # Reset password
    # -------------------------------------------------------------------------

    @staticmethod
    def reset_password(db: Session, email: str, code: str, new_password: str) -> None:
        user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")

        hashed = hashlib.sha256(code.encode()).hexdigest()
        reset = (
            db.query(PasswordReset)
            .filter(
                PasswordReset.user_id == user.id,
                PasswordReset.code_hash == hashed,
                PasswordReset.used == False,
            )
            .first()
        )

        if not reset or reset.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired code")

        reset.used = True
        user.password_hash = hash_password(new_password)

        # Revoke all refresh tokens — force re-login everywhere
        db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update({"revoked": True})

        db.commit()


auth_service = AuthService()
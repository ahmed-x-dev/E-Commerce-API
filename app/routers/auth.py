# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, Response, Request ,status
from sqlalchemy.orm import Session
from app.core.rate_limiter import RateLimiter
from app.db.schemas.auth_schema import EmailVerificationRequest, LoginRequest, TokenResponse, PasswordResetRequest, SendPasswordResetEmailRequest 
from app.db.schemas.user_schema import UserCreate, UserRead
from app.db.session import get_db
from app.security.dependencies import get_current_user
from app.services.auth_service import AuthService


from app.core.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])



@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    data: UserCreate, 
    db: Session = Depends(get_db)
    ):

    return  AuthService.register(db, data)




@router.post(
    "/login", 
    response_model=TokenResponse, 
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(key_prefix="login", max_requests=5, window_seconds=60))]
    )
def login(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
    ):

    access_token, refresh_token = AuthService.login(db, data)

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.http_only, 
        samesite="none"
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )



@router.post("/refresh", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
    ):
        
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    access_token, refresh_token = AuthService.refresh(db, refresh_token)

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.http_only,  # True in production
        samesite="none"
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )




@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 1. Get the refresh token from the cookie
    refresh_token = request.cookies.get("refresh_token")

    # 2. Revoke it in the database
    if refresh_token:
        AuthService.logout(db, refresh_token)

    # 3. Tell the browser to delete the cookie
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="none",
        secure=settings.http_only 
    )

    return {"message": "Logged out successfully"}




@router.post(
        "/verify-email", 
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(RateLimiter(key_prefix="verify-email", max_requests=5, window_seconds=60))]
        )
def verify_email(
    data: EmailVerificationRequest,
    db: Session = Depends(get_db)
    ):

    AuthService.verify_email(db, data)
    return {"message": "Email verified successfully"}




@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
def request_password_reset(
    data: SendPasswordResetEmailRequest,
    db: Session = Depends(get_db)
    ):

    AuthService.forgot_password(db, data.email)
    return {"message": "Password reset email sent if the email is registered"}




@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
    ):

    AuthService.reset_password(db,data.email, data.code, data.new_password)
    return {"message": "Password reset successfully"}
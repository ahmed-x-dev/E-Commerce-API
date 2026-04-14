from pydantic import EmailStr, Field

from app.db.schemas.common import ORMBaseModel


class LoginRequest(ORMBaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(ORMBaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(ORMBaseModel):
    sub: str | None = None
    exp: int | None = None


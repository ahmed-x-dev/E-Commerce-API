from datetime import datetime

from pydantic import EmailStr, Field

from app.db.schemas.common import ORMBaseModel


class UserBase(ORMBaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(ORMBaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


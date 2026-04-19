from datetime import datetime

from pydantic import EmailStr, Field

from app.db.schemas.common import ORMBaseModel

from enum import Enum 

class UserRole(str, Enum):
    admin = "admin"
    staff = "staff"
    customer = "customer"

class UserBase(ORMBaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=50)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(ORMBaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


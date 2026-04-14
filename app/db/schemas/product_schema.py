from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.db.schemas.common import ORMBaseModel


class ProductBase(ORMBaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ORMBaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=3000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock_quantity: int | None = Field(default=None, ge=0)


class ProductRead(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime


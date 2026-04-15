from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field

from app.db.schemas.common import ORMBaseModel


class CartStatus(str, Enum):
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    ABANDONED = "abandoned"


class ShoppingCartCreate(ORMBaseModel):
    user_id: int = Field(gt=0)
    status: CartStatus = CartStatus.ACTIVE


class ShoppingCartUpdate(ORMBaseModel):
    status: CartStatus | None = None


class CartItemCreate(ORMBaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(ge=1)


class CartItemUpdate(ORMBaseModel):
    quantity: int = Field(ge=1)


class CartItemRead(ORMBaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
    price_at_time: Decimal
    created_at: datetime
    updated_at: datetime


class ShoppingCartRead(ORMBaseModel):
    id: int
    user_id: int
    status: CartStatus
    created_at: datetime
    updated_at: datetime
    items: list[CartItemRead] = Field(default_factory=list)

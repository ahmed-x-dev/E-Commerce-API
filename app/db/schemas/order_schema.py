from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import Field

from app.db.schemas.common import ORMBaseModel


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELED = "canceled"


class PaymentMethod(str, Enum):
    CARD = "card"
    CASH_ON_DELIVERY = "cash_on_delivery"
    WALLET = "wallet"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class CheckoutRequest(ORMBaseModel):
    cart_id: int = Field(gt=0)
    payment_method: PaymentMethod = PaymentMethod.CARD


class OrderCreate(ORMBaseModel):
    user_id: int = Field(gt=0)
    total_amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    status: OrderStatus = OrderStatus.PENDING


class OrderUpdate(ORMBaseModel):
    total_amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    status: OrderStatus | None = None


class PaymentCreate(ORMBaseModel):
    order_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    method: PaymentMethod
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: str | None = Field(default=None, max_length=255)


class PaymentUpdate(ORMBaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    method: PaymentMethod | None = None
    status: PaymentStatus | None = None
    transaction_id: str | None = Field(default=None, max_length=255)


class PaymentRead(ORMBaseModel):
    id: int
    order_id: int
    amount: Decimal
    method: PaymentMethod
    status: PaymentStatus
    transaction_id: str | None = None
    created_at: datetime
    updated_at: datetime


class OrderRead(ORMBaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    payments: list[PaymentRead] = Field(default_factory=list)

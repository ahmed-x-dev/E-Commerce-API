from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:

    from app.db.models.user_model import User
    from app.db.models.cart_item_model import CartItem


class CartStatus(str, enum.Enum):
    ACTIVE = "active"
    CHECKED_OUT = "checked_out"
    ABANDONED = "abandoned"


class ShoppingCart(Base, TimestampMixin):
    __tablename__ = "shopping_carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[CartStatus] = mapped_column(
        SQLEnum(CartStatus, name="cart_status"),
        nullable=False,
        default=CartStatus.ACTIVE,
    )

    user: Mapped["User"] = relationship(back_populates="shopping_carts")
    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
    )


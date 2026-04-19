from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin
from app.db.schemas.user_schema import UserRole

# Avoid circular imports for type checking
if TYPE_CHECKING: 
    from app.db.models.shopping_cart_model import ShoppingCart
    from app.db.models.order_model import Order
    

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"),default=UserRole.customer,nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    shopping_carts: Mapped[list["ShoppingCart"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
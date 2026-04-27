from __future__ import annotations

from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.order_model import Order, OrderStatus as OrderModelStatus
from app.db.models.payment_model import Payment, PaymentMethod as PaymentModelMethod, PaymentStatus as PaymentModelStatus
from app.db.models.product_model import Product
from app.db.models.shopping_cart_model import CartStatus, ShoppingCart
from app.db.schemas.order_schema import CheckoutRequest, OrderRead, OrderUpdate


class OrderService:
    def _get_order(self, db: Session, order_id: int) -> Order | None:
        """Fetch an order with related payments by ID."""
        stmt = (
            select(Order)
            .options(selectinload(Order.payments))
            .where(Order.id == order_id)
        )
        return db.execute(stmt).scalar_one_or_none()

    def checkout(self, db: Session, user_id: int, data: CheckoutRequest) -> OrderRead:
        """Create an order from an active cart, create payment row, and reduce stock."""
        cart_stmt = (
            select(ShoppingCart)
            .options(selectinload(ShoppingCart.items))
            .where(
                ShoppingCart.id == data.cart_id,
                ShoppingCart.user_id == user_id,
            )
        )
        cart = db.execute(cart_stmt).scalar_one_or_none()

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        if cart.status != CartStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only active carts can be checked out",
            )

        if not cart.items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot checkout an empty cart",
            )

        total_amount = Decimal("0")
        stock_updates: list[tuple[Product, int]] = []

        for item in cart.items:
            product = db.get(Product, item.product_id)
            if not product or product.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product {item.product_id} is unavailable",
                )

            if item.quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for product {product.id}",
                )

            total_amount += item.price_at_time * item.quantity
            stock_updates.append((product, item.quantity))

        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderModelStatus.PENDING,
        )
        db.add(order)
        db.flush()

        payment = Payment(
            order_id=order.id,
            amount=total_amount,
            method=PaymentModelMethod(data.payment_method.value),
            status=PaymentModelStatus.PENDING,
        )
        db.add(payment)

        for product, quantity in stock_updates:
            product.stock_quantity -= quantity

        cart.status = CartStatus.CHECKED_OUT

        db.commit()
        created_order = self._get_order(db, order.id)
        if not created_order:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Order creation failed")

        return OrderRead.model_validate(created_order)

    def get_orders_for_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[OrderRead]:
        """Return paginated orders that belong to a specific user."""
        stmt = (
            select(Order)
            .options(selectinload(Order.payments))
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = db.execute(stmt).scalars().all()
        return [OrderRead.model_validate(order) for order in orders]

    def get_all_orders(self, db: Session, skip: int = 0, limit: int = 100) -> list[OrderRead]:
        """Return paginated orders across all users for back-office views."""
        stmt = (
            select(Order)
            .options(selectinload(Order.payments))
            .order_by(Order.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        orders = db.execute(stmt).scalars().all()
        return [OrderRead.model_validate(order) for order in orders]

    def get_order_for_user(self, db: Session, order_id: int, user_id: int) -> OrderRead:
        """Return an order only if it belongs to the requesting user."""
        order = self._get_order(db, order_id)
        if not order or order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderRead.model_validate(order)

    def get_order_admin(self, db: Session, order_id: int) -> OrderRead:
        """Return any order by ID for privileged staff/admin access."""
        order = self._get_order(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderRead.model_validate(order)

    def update_order(self, db: Session, order_id: int, data: OrderUpdate) -> OrderRead:
        """Update order fields and keep related payment status aligned with order status."""
        order = db.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        update_data = data.model_dump(exclude_unset=True)

        if "total_amount" in update_data:
            order.total_amount = update_data["total_amount"]

        if "status" in update_data:
            new_status = OrderModelStatus(update_data["status"])
            order.status = new_status

            for payment in order.payments:
                if new_status == OrderModelStatus.PAID:
                    payment.status = PaymentModelStatus.SUCCEEDED
                elif new_status == OrderModelStatus.FAILED:
                    payment.status = PaymentModelStatus.FAILED
                elif new_status == OrderModelStatus.CANCELED:
                    payment.status = PaymentModelStatus.CANCELED

        db.commit()
        updated_order = self._get_order(db, order.id)
        if not updated_order:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Order update failed")
        return OrderRead.model_validate(updated_order)


order_service = OrderService()

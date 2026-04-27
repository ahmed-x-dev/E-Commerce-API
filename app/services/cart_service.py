from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.cart_item_model import CartItem
from app.db.models.product_model import Product
from app.db.models.shopping_cart_model import CartStatus, ShoppingCart
from app.db.schemas.cart_schema import CartItemCreate, CartItemUpdate, ShoppingCartRead


class CartService:
    def _get_active_cart(self, db: Session, user_id: int, create_if_missing: bool = False) -> ShoppingCart:
        """Fetch the user's active cart, optionally creating one if it does not exist."""
        stmt = (
            select(ShoppingCart)
            .options(selectinload(ShoppingCart.items))
            .where(
                ShoppingCart.user_id == user_id,
                ShoppingCart.status == CartStatus.ACTIVE,
            )
        )
        cart = db.execute(stmt).scalar_one_or_none()

        if cart:
            return cart

        if not create_if_missing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active cart not found")

        cart = ShoppingCart(user_id=user_id, status=CartStatus.ACTIVE)
        db.add(cart)
        db.commit()
        return self._get_cart_by_id(db, cart.id)

    def _get_cart_by_id(self, db: Session, cart_id: int) -> ShoppingCart:
        """Load a cart by ID with its items or raise 404 if missing."""
        stmt = (
            select(ShoppingCart)
            .options(selectinload(ShoppingCart.items))
            .where(ShoppingCart.id == cart_id)
        )
        cart = db.execute(stmt).scalar_one_or_none()
        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")
        return cart

    def _get_product_or_404(self, db: Session, product_id: int) -> Product:
        """Fetch a non-deleted product or raise 404 when unavailable."""
        product = db.get(Product, product_id)
        if not product or product.is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def _get_owned_cart_item(self, db: Session, user_id: int, item_id: int) -> CartItem:
        """Fetch a cart item only if it belongs to the user's active cart."""
        stmt = (
            select(CartItem)
            .join(ShoppingCart, ShoppingCart.id == CartItem.cart_id)
            .where(
                CartItem.id == item_id,
                ShoppingCart.user_id == user_id,
                ShoppingCart.status == CartStatus.ACTIVE,
            )
        )
        item = db.execute(stmt).scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        return item

    def get_current_cart(self, db: Session, user_id: int) -> ShoppingCartRead:
        """Return the user's active cart, creating it automatically if missing."""
        cart = self._get_active_cart(db, user_id=user_id, create_if_missing=True)
        return ShoppingCartRead.model_validate(cart)

    def add_item(self, db: Session, user_id: int, item_data: CartItemCreate) -> ShoppingCartRead:
        """Add a product to cart or increase quantity if that product already exists in cart."""
        cart = self._get_active_cart(db, user_id=user_id, create_if_missing=True)
        product = self._get_product_or_404(db, item_data.product_id)

        if item_data.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock",
            )

        stmt = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id,
        )
        existing_item = db.execute(stmt).scalar_one_or_none()

        if existing_item:
            new_quantity = existing_item.quantity + item_data.quantity
            if new_quantity > product.stock_quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Requested quantity exceeds available stock",
                )
            existing_item.quantity = new_quantity
            existing_item.price_at_time = product.price
        else:
            db.add(
                CartItem(
                    cart_id=cart.id,
                    product_id=item_data.product_id,
                    quantity=item_data.quantity,
                    price_at_time=product.price,
                )
            )

        db.commit()
        refreshed_cart = self._get_cart_by_id(db, cart.id)
        return ShoppingCartRead.model_validate(refreshed_cart)

    def update_item(self, db: Session, user_id: int, item_id: int, item_data: CartItemUpdate) -> ShoppingCartRead:
        """Update quantity for a specific cart item after stock validation."""
        item = self._get_owned_cart_item(db, user_id=user_id, item_id=item_id)
        product = self._get_product_or_404(db, item.product_id)

        if item_data.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock",
            )

        item.quantity = item_data.quantity
        item.price_at_time = product.price

        db.commit()
        refreshed_cart = self._get_cart_by_id(db, item.cart_id)
        return ShoppingCartRead.model_validate(refreshed_cart)

    def remove_item(self, db: Session, user_id: int, item_id: int) -> ShoppingCartRead:
        """Remove one item from the user's active cart and return the updated cart."""
        item = self._get_owned_cart_item(db, user_id=user_id, item_id=item_id)
        cart_id = item.cart_id

        db.delete(item)
        db.commit()

        refreshed_cart = self._get_cart_by_id(db, cart_id)
        return ShoppingCartRead.model_validate(refreshed_cart)

    def clear_current_cart(self, db: Session, user_id: int) -> ShoppingCartRead:
        """Remove all items from the user's active cart."""
        cart = self._get_active_cart(db, user_id=user_id, create_if_missing=True)

        stmt = select(CartItem).where(CartItem.cart_id == cart.id)
        items = db.execute(stmt).scalars().all()
        for item in items:
            db.delete(item)

        db.commit()
        refreshed_cart = self._get_cart_by_id(db, cart.id)
        return ShoppingCartRead.model_validate(refreshed_cart)


cart_service = CartService()

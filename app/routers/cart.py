from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.schemas.cart_schema import CartItemCreate, CartItemUpdate, ShoppingCartRead
from app.db.session import get_db
from app.security.dependencies import get_current_user
from app.services.cart_service import cart_service


router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=ShoppingCartRead, status_code=status.HTTP_200_OK)
def get_current_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return the authenticated user's active shopping cart."""
    return cart_service.get_current_cart(db, user_id=current_user.id)


@router.post("/items", response_model=ShoppingCartRead, status_code=status.HTTP_200_OK)
def add_item_to_cart(
    item_data: CartItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Add a product to the authenticated user's active cart."""
    return cart_service.add_item(db, user_id=current_user.id, item_data=item_data)


@router.put("/items/{item_id}", response_model=ShoppingCartRead, status_code=status.HTTP_200_OK)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update quantity and price snapshot for one cart item."""
    return cart_service.update_item(db, user_id=current_user.id, item_id=item_id, item_data=item_data)


@router.delete("/items/{item_id}", response_model=ShoppingCartRead, status_code=status.HTTP_200_OK)
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove a single item from the authenticated user's cart."""
    return cart_service.remove_item(db, user_id=current_user.id, item_id=item_id)


@router.delete("/items", response_model=ShoppingCartRead, status_code=status.HTTP_200_OK)
def clear_current_cart(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Remove all items from the authenticated user's active cart."""
    return cart_service.clear_current_cart(db, user_id=current_user.id)

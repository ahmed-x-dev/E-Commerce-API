from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.schemas.order_schema import CheckoutRequest, OrderRead
from app.db.session import get_db
from app.security.dependencies import get_current_user
from app.services.order_service import order_service


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def checkout(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Create an order from a cart and initialize its payment record."""
    return order_service.checkout(db, user_id=current_user.id, data=data)


@router.get("/", response_model=list[OrderRead], status_code=status.HTTP_200_OK)
def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List orders that belong to the authenticated user."""
    return order_service.get_orders_for_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a single order if it belongs to the authenticated user."""
    return order_service.get_order_for_user(db, order_id=order_id, user_id=current_user.id)

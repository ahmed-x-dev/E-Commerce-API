from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.schemas.order_schema import OrderRead, OrderUpdate
from app.db.session import get_db
from app.services.order_service import order_service


router = APIRouter()


@router.get("/", response_model=list[OrderRead], status_code=status.HTTP_200_OK)
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all orders for staff/admin users."""
    return order_service.get_all_orders(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK)
def get_order_admin(
    order_id: int,
    db: Session = Depends(get_db),
):
    """Get any order by ID for staff/admin users."""
    return order_service.get_order_admin(db, order_id=order_id)


@router.put("/{order_id}", response_model=OrderRead, status_code=status.HTTP_200_OK)
def update_order(
    order_id: int,
    data: OrderUpdate,
    db: Session = Depends(get_db),
):
    """Update order fields such as status and total amount (staff/admin)."""
    return order_service.update_order(db, order_id=order_id, data=data)

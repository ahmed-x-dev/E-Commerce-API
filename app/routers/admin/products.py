from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rate_limiter import RateLimiter
from app.db.schemas.product_schema import ProductCreate, ProductRead, ProductUpdate
from app.db.session import get_db
from app.services.product_service import product_service


router = APIRouter()


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(key_prefix="create_product", max_requests=10, window_seconds=60))],
)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    """Create a new product (staff/admin only)."""
    return product_service.create_product(db, product_data)


@router.put("/{product_id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    """Update a product (staff/admin only)."""
    updated_product = product_service.update_product(db, product_id, product_data)
    if not updated_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return updated_product


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Delete a product (staff/admin only)."""
    success = product_service.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return {"message": "Product deleted successfully"}

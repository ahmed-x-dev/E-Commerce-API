from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.db.session import get_db
from app.db.schemas.product_schema import ProductRead
from app.services.product_service import product_service


router = APIRouter(prefix="/products", tags=["products"])


# ------------------------------------
# Read Products(with pagination)
# ------------------------------------
@router.get("/", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
def get_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of products to return"),
    db: Session = Depends(get_db)
):
    """Get all products with pagination"""
    return product_service.get_products(db, skip=skip, limit=limit)



# ------------------------------------
# Get products that are currently in stock
# ------------------------------------
@router.get("/in-stock", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
def get_products_in_stock(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of products to return"),
    db: Session = Depends(get_db)
):
    """Get products that are currently in stock"""
    return product_service.get_products_in_stock(db, skip=skip, limit=limit)




# ------------------------------------
#  search for porducts by name or description
# ------------------------------------
@router.get("/search", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
def search_products(
    q: str = Query(..., min_length=1, description="Search query for product name or description"),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of products to return"),
    db: Session = Depends(get_db)
):
    """Search products by name or description"""
    return product_service.search_products(db, query=q, skip=skip, limit=limit)


# ------------------------------------
#  Get products within a price range
# ------------------------------------
@router.get("/price-range", response_model=List[ProductRead], status_code=status.HTTP_200_OK)
def get_products_by_price_range(
    min_price: Decimal = Query(..., gt=0, description="Minimum price"),
    max_price: Decimal = Query(..., gt=0, description="Maximum price"),
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of products to return"),
    db: Session = Depends(get_db)
):
    """Get products within a price range"""
    if min_price >= max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price must be less than max_price"
        )
    return product_service.get_products_by_price_range(db, min_price=float(min_price), max_price=float(max_price), skip=skip, limit=limit)



# ------------------------------------
#  get a product by ID
# ------------------------------------
@router.get("/{product_id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get a product by ID"""
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

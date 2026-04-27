from fastapi import APIRouter, Depends

from app.security.dependencies import get_staff_user

from . import orders, products, users


router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_staff_user)])

router.include_router(users.router , prefix="/users")
router.include_router(products.router, prefix="/products")
router.include_router(orders.router, prefix="/orders")

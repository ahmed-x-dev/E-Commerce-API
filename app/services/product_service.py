from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.db.models.product_model import Product
from app.db.schemas.product_schema import ProductCreate, ProductUpdate, ProductRead


class ProductService:

    def create_product(self, db: Session, product_data: ProductCreate) -> ProductRead:
        """Create a new product"""
        db_product = Product(**product_data.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return ProductRead.model_validate(db_product)

    def get_product_by_id(self, db: Session, product_id: int) -> Optional[ProductRead]:
        """Get a product by ID"""
        product = db.get(Product, product_id)
        if product and not product.is_deleted:
            return ProductRead.model_validate(product)
        return None

    def get_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProductRead]:
        """Get all active products with pagination"""
        stmt = (
            select(Product)
            .where(Product.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        products = db.execute(stmt).scalars().all()
        return [ProductRead.model_validate(p) for p in products]

    def update_product(self, db: Session, product_id: int, product_data: ProductUpdate) -> Optional[ProductRead]:
        """Update a product"""
        db_product = db.get(Product, product_id)
        if not db_product or db_product.is_deleted:
            return None

        update_data = product_data.model_dump(exclude_unset=True)  # only include fields that were provided
        for field, value in update_data.items():
            setattr(db_product, field, value)

        db.commit()
        db.refresh(db_product)
        return ProductRead.model_validate(db_product)

    def delete_product(self, db: Session, product_id: int) -> bool:
        """Soft delete a product by setting is_deleted flag"""
        db_product = db.get(Product, product_id)
        if not db_product or db_product.is_deleted:
            return False

        db_product.is_deleted = True
        db.commit()
        return True

    def search_products(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[ProductRead]:
        """Search active products by name or description"""
        search_pattern = f"%{query}%" # for case-insensitive partial match
        stmt = (
            select(Product)
            .where(
                Product.is_deleted == False,
                (Product.name.ilike(search_pattern)) |
                (Product.description.ilike(search_pattern))
            )
            .offset(skip)
            .limit(limit)
        )
        products = db.execute(stmt).scalars().all()
        return [ProductRead.model_validate(p) for p in products]

    def get_products_by_price_range(self, db: Session, min_price: float, max_price: float, skip: int = 0, limit: int = 100) -> List[ProductRead]:
        """Get active products within a price range"""
        stmt = (
            select(Product)
            .where(
                Product.is_deleted == False,
                Product.price >= min_price,
                Product.price <= max_price
            )
            .offset(skip)
            .limit(limit)
        )
        products = db.execute(stmt).scalars().all()
        return [ProductRead.model_validate(p) for p in products]

    def get_products_in_stock(self, db: Session, skip: int = 0, limit: int = 100) -> List[ProductRead]:
        """Get active products that are in stock"""
        stmt = (
            select(Product)
            .where(
                Product.is_deleted == False,
                Product.stock_quantity > 0
            )
            .offset(skip)
            .limit(limit)
        )
        products = db.execute(stmt).scalars().all()
        return [ProductRead.model_validate(p) for p in products]

    def get_products_by_category(self, db: Session, category_id: int, skip: int = 0, limit: int = 100) -> List[ProductRead]:
        """Get active products by category"""
        stmt = (
            select(Product)
            .where(
                Product.is_deleted == False,
                Product.category_id == category_id
            )
            .offset(skip)
            .limit(limit)
        )
        products = db.execute(stmt).scalars().all()
        return [ProductRead.model_validate(p) for p in products]

    def get_products_count(self, db: Session) -> int:
        """Get total count of active products (useful for pagination metadata)"""
        stmt = select(Product).where(Product.is_deleted == False)
        return len(db.execute(stmt).scalars().all())


# Create a global instance of the service
product_service = ProductService()
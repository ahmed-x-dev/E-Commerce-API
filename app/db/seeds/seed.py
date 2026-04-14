from __future__ import annotations

import argparse
import os
import random
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.cart_item_model import CartItem
from app.db.models.order_model import Order, OrderStatus
from app.db.models.payment_model import Payment, PaymentMethod, PaymentStatus
from app.db.models.product_model import Product
from app.db.models.shopping_cart_model import CartStatus, ShoppingCart
from app.db.models.user_model import User
from app.db.session import SessionLocal
from app.security.hashing import hash_password

FAKER_SEED = 20260414

BASE_PRODUCTS: list[dict[str, Decimal | int | str]] = [
    {
        "name": "Wireless Mechanical Keyboard",
        "description": "Hot-swappable keyboard with RGB backlight and Bluetooth support.",
        "price": Decimal("89.99"),
        "stock_quantity": 45,
    },
    {
        "name": "Ergonomic Office Mouse",
        "description": "Low-latency mouse designed for long work sessions.",
        "price": Decimal("34.50"),
        "stock_quantity": 120,
    },
    {
        "name": "USB-C Hub 7-in-1",
        "description": "Hub with HDMI, USB-A, USB-C, and card reader ports.",
        "price": Decimal("49.00"),
        "stock_quantity": 70,
    },
    {
        "name": "1080p Webcam",
        "description": "Noise-reduction microphone and auto-light correction.",
        "price": Decimal("58.25"),
        "stock_quantity": 55,
    },
    {
        "name": "Laptop Stand",
        "description": "Aluminum adjustable stand for 13-17 inch laptops.",
        "price": Decimal("29.99"),
        "stock_quantity": 90,
    },
]


@dataclass
class SeedStats:
    users_created: int = 0
    users_updated: int = 0
    products_created: int = 0
    products_updated: int = 0
    carts_created: int = 0
    cart_items_created: int = 0
    cart_items_updated: int = 0
    orders_created: int = 0
    payments_created: int = 0


class SimpleFactory:
    """Fallback fake-data factory if Faker is unavailable in the runtime."""

    def __init__(self, seed: int) -> None:
        self.rng = random.Random(seed)
        self.first_names = [
            "Mia",
            "Noah",
            "Liam",
            "Ava",
            "Mason",
            "Sara",
            "Omar",
            "Nora",
            "Kareem",
            "Layla",
        ]
        self.last_names = [
            "Ali",
            "Hassan",
            "Ibrahim",
            "Saad",
            "Youssef",
            "Karim",
            "Adel",
            "Nassar",
            "Fahmy",
            "Salem",
        ]
        self.words = [
            "premium",
            "smart",
            "durable",
            "lightweight",
            "compact",
            "pro",
            "elite",
            "wireless",
            "eco",
            "secure",
        ]

    def name(self) -> str:
        return f"{self.rng.choice(self.first_names)} {self.rng.choice(self.last_names)}"

    def word(self) -> str:
        return self.rng.choice(self.words)

    def sentence(self, nb_words: int = 10) -> str:
        sentence_words = [self.word() for _ in range(nb_words)]
        sentence = " ".join(sentence_words)
        return sentence.capitalize() + "."


def build_factory(seed: int):
    try:
        from faker import Faker
    except ImportError:
        return SimpleFactory(seed)

    Faker.seed(seed)
    factory = Faker()
    factory.seed_instance(seed)
    return factory


def upsert_user(
    session: Session,
    stats: SeedStats,
    *,
    email: str,
    name: str,
    password: str,
) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user:
        changed = False
        if user.name != name:
            user.name = name
            changed = True
        if changed:
            stats.users_updated += 1
        return user

    user = User(email=email, name=name, password_hash=hash_password(password))
    session.add(user)
    session.flush()
    stats.users_created += 1
    return user


def upsert_product(
    session: Session,
    stats: SeedStats,
    *,
    name: str,
    description: str,
    price: Decimal,
    stock_quantity: int,
) -> Product:
    product = session.scalar(select(Product).where(Product.name == name))
    if product:
        changed = False
        if product.description != description:
            product.description = description
            changed = True
        if product.price != price:
            product.price = price
            changed = True
        if product.stock_quantity != stock_quantity:
            product.stock_quantity = stock_quantity
            changed = True
        if changed:
            stats.products_updated += 1
        return product

    product = Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity,
    )
    session.add(product)
    session.flush()
    stats.products_created += 1
    return product


def get_or_create_active_cart(session: Session, stats: SeedStats, user_id: int) -> ShoppingCart:
    cart = session.scalar(
        select(ShoppingCart).where(
            ShoppingCart.user_id == user_id,
            ShoppingCart.status == CartStatus.ACTIVE,
        )
    )
    if cart:
        return cart

    cart = ShoppingCart(user_id=user_id, status=CartStatus.ACTIVE)
    session.add(cart)
    session.flush()
    stats.carts_created += 1
    return cart


def upsert_cart_item(
    session: Session,
    stats: SeedStats,
    *,
    cart_id: int,
    product_id: int,
    quantity: int,
    price_at_time: Decimal,
) -> CartItem:
    cart_item = session.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
    )
    if cart_item:
        changed = False
        if cart_item.quantity != quantity:
            cart_item.quantity = quantity
            changed = True
        if cart_item.price_at_time != price_at_time:
            cart_item.price_at_time = price_at_time
            changed = True
        if changed:
            stats.cart_items_updated += 1
        return cart_item

    cart_item = CartItem(
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
        price_at_time=price_at_time,
    )
    session.add(cart_item)
    session.flush()
    stats.cart_items_created += 1
    return cart_item


def create_order_with_payment_if_missing(
    session: Session,
    stats: SeedStats,
    *,
    user_id: int,
    amount: Decimal,
    transaction_id: str,
    method: PaymentMethod = PaymentMethod.CARD,
) -> None:
    existing_payment = session.scalar(
        select(Payment).where(Payment.transaction_id == transaction_id)
    )
    if existing_payment:
        return

    order = Order(
        user_id=user_id,
        total_amount=amount,
        status=OrderStatus.PAID,
    )
    session.add(order)
    session.flush()
    stats.orders_created += 1

    payment = Payment(
        order_id=order.id,
        amount=amount,
        method=method,
        status=PaymentStatus.SUCCEEDED,
        transaction_id=transaction_id,
    )
    session.add(payment)
    session.flush()
    stats.payments_created += 1


def run_prod_seed(session: Session, stats: SeedStats) -> None:
    admin_email = os.getenv("SEED_ADMIN_EMAIL", "admin@ecommerce.local")
    admin_name = os.getenv("SEED_ADMIN_NAME", "System Admin")
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin12345!")

    # Current schema has no role column yet; we seed the default admin account identity now.
    upsert_user(
        session,
        stats,
        email=admin_email,
        name=admin_name,
        password=admin_password,
    )

    for product_data in BASE_PRODUCTS:
        upsert_product(
            session,
            stats,
            name=str(product_data["name"]),
            description=str(product_data["description"]),
            price=Decimal(str(product_data["price"])),
            stock_quantity=int(product_data["stock_quantity"]),
        )


def run_dev_seed(session: Session, stats: SeedStats, user_count: int, product_count: int) -> None:
    run_prod_seed(session, stats)

    rng = random.Random(FAKER_SEED)
    fake = build_factory(FAKER_SEED)

    users: list[User] = []
    for i in range(1, user_count + 1):
        user = upsert_user(
            session,
            stats,
            email=f"dev_user_{i}@example.com",
            name=fake.name(),
            password="DevPassword123!",
        )
        users.append(user)

    products: list[Product] = []
    for i in range(1, product_count + 1):
        product = upsert_product(
            session,
            stats,
            name=f"Dev Product {i:03d} {fake.word().title()}",
            description=fake.sentence(nb_words=14),
            price=Decimal(str(round(rng.uniform(6.0, 300.0), 2))),
            stock_quantity=rng.randint(5, 250),
        )
        products.append(product)

    for user in users:
        cart = get_or_create_active_cart(session, stats, user.id)
        sample_size = min(4, len(products))
        for product in rng.sample(products, k=sample_size):
            upsert_cart_item(
                session,
                stats,
                cart_id=cart.id,
                product_id=product.id,
                quantity=rng.randint(1, 4),
                price_at_time=product.price,
            )

    paid_users = users[: min(10, len(users))]
    for index, user in enumerate(paid_users, start=1):
        amount = Decimal(str(round(rng.uniform(20.0, 900.0), 2)))
        create_order_with_payment_if_missing(
            session,
            stats,
            user_id=user.id,
            amount=amount,
            transaction_id=f"DEV-TXN-{index:04d}-{user.email.replace('@', '_').replace('.', '_')}",
            method=PaymentMethod.CARD,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed database data for local/dev environments.")
    parser.add_argument(
        "--mode",
        choices=("prod", "dev"),
        default="dev",
        help="prod: essential seed data, dev: larger fake dataset",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=25,
        help="number of dev users to seed when mode=dev",
    )
    parser.add_argument(
        "--products",
        type=int,
        default=60,
        help="number of dev products to seed when mode=dev",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="required to run prod seeding when ENVIRONMENT=production",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.mode == "dev" and settings.environment == "production":
        raise RuntimeError("Dev seed is blocked when ENVIRONMENT=production.")

    if args.mode == "prod" and settings.environment == "production" and not args.force:
        raise RuntimeError("Use --force to run prod seed when ENVIRONMENT=production.")

    stats = SeedStats()
    with SessionLocal() as session:
        try:
            if args.mode == "prod":
                run_prod_seed(session, stats)
            else:
                run_dev_seed(session, stats, user_count=args.users, product_count=args.products)
            session.commit()
        except Exception:
            session.rollback()
            raise

    print("Seed completed.")
    print(f"mode={args.mode}, environment={settings.environment}")
    print(
        "users(created/updated)={}/{} | products(created/updated)={}/{} | "
        "carts(created)={} | cart_items(created/updated)={}/{} | "
        "orders(created)={} | payments(created)={}".format(
            stats.users_created,
            stats.users_updated,
            stats.products_created,
            stats.products_updated,
            stats.carts_created,
            stats.cart_items_created,
            stats.cart_items_updated,
            stats.orders_created,
            stats.payments_created,
        )
    )


if __name__ == "__main__":
    main()

import argparse
import random
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.models.product_model import Product
from app.db.session import SessionLocal
# Assuming build_factory and SeedStats are in your original file or accessible
from app.db.seeds.seed import build_factory, SeedStats, upsert_product, FAKER_SEED 

def seed_fake_products(session: Session, count: int):
    stats = SeedStats()
    rng = random.Random(FAKER_SEED)
    fake = build_factory(FAKER_SEED)

    print(f"--- Generating {count} fake products ---")

    for i in range(1, count + 1):
        # Generate random attributes
        name = f"Fake Product {i:03d} {fake.word().title()}"
        description = fake.sentence(nb_words=12)
        price = Decimal(str(round(rng.uniform(5.0, 500.0), 2)))
        stock = rng.randint(0, 100)

        upsert_product(
            session,
            stats,
            name=name,
            description=description,
            price=price,
            stock_quantity=stock,
        )

    session.commit()
    print(f"Finished: Created {stats.products_created}, Updated {stats.products_updated}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=50, help="How many products to create")
    args = parser.parse_args()

    with SessionLocal() as session:
        seed_fake_products(session, args.count)
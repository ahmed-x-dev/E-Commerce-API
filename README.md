# E-Commerce API

FastAPI e-commerce backend with PostgreSQL, SQLAlchemy, Alembic, and Stripe integration.

## Setup

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Run Database

```powershell
docker compose up -d db
```

## Migrations

```powershell
alembic upgrade head
```

## Seed Data

This project supports two seed modes:

- `prod`: essential seed data only (admin account + baseline products)
- `dev`: larger fake dataset for local development/testing

Seed commands:

```powershell
# Production-safe seed (essential records only)
python -m app.db.seeds.seed --mode prod

# Development seed (fake data, reproducible and idempotent)
python -m app.db.seeds.seed --mode dev --users 25 --products 60
```

Important safety rule:

- Never run `--mode dev` when `ENVIRONMENT=production`.
- The seed script blocks this automatically.

Optional seed env vars:

- `SEED_ADMIN_EMAIL` (default: `admin@ecommerce.local`)
- `SEED_ADMIN_NAME` (default: `System Admin`)
- `SEED_ADMIN_PASSWORD` (default: `Admin12345!`)

## Run API

```powershell
uvicorn main:app --reload
```

# E-Commerce API

A comprehensive FastAPI e-commerce backend platform with user authentication, product catalog, shopping cart, order management, and Stripe payment integration.

**Project URL:** [roadmap.sh/projects/ecommerce-api](https://roadmap.sh/projects/ecommerce-api)

## Overview

This project implements a full-featured e-commerce API with JWT authentication, complex data models, external service integration (Stripe), and an admin panel for inventory management. It's designed to teach you how to build a logic-heavy application with multiple moving parts.

### Key Features

- ✅ **User Authentication** - JWT-based registration and login with email verification
- ✅ **Product Catalog** - Browse, search, and filter products with pagination
- ✅ **Shopping Cart** - Add, remove, and manage items in the cart
- ✅ **Order Management** - Checkout process and order history
- ✅ **Payment Processing** - Stripe integration for secure payments (card & wallet)
- ✅ **Admin Panel** - Manage products, inventory, users, and orders
- ✅ **Security** - Rate limiting, CORS, security headers, input validation
- ✅ **Database Migrations** - Alembic for version-controlled schema management
- ✅ **Caching** - Redis for session management and caching
- ✅ **Logging** - Structured logging for debugging and monitoring

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | FastAPI (Python 3.12) |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy 2.0+ |
| **Migrations** | Alembic |
| **Authentication** | JWT (PyJWT) |
| **Validation** | Pydantic v2 |
| **Payment** | Stripe API |
| **Caching** | Redis |
| **Rate Limiting** | Custom middleware |
| **Containerization** | Docker & Docker Compose |

## Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis (optional, for caching)
- Git
- Postman or similar tool for API testing
- Stripe account (for payment processing)

## Setup & Installation

### 1. Clone the Repository

```powershell
git clone <repository-url>
cd "E-Commerce API"
```

### 2. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root with the following variables:

```env
# Application
APP_NAME=E-Commerce API
ENVIRONMENT=development
DEBUG=true
API_V1_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/ecommerce_api

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Seed Data
SEED_ADMIN_EMAIL=admin@ecommerce.local
SEED_ADMIN_NAME=System Admin
SEED_ADMIN_PASSWORD=Admin12345!
```

### 5. Start Database with Docker

```powershell
docker compose up -d db
```

### 6. Run Database Migrations

```powershell
alembic upgrade head
```

### 7. Seed Initial Data

```powershell
# Production-safe seed (admin account + baseline products)
python -m app.db.seeds.seed --mode prod

# Development seed (fake data for testing)
python -m app.db.seeds.seed --mode dev --users 25 --products 60
```

### 8. Run the API

```powershell
# Development mode with hot reload
uvicorn main:app --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Access API Documentation

- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **OpenAPI JSON:** http://localhost:8000/api/v1/openapi.json

## Docker Deployment

### Run Everything with Docker Compose

```powershell
docker compose up
```

This starts:
- PostgreSQL database
- API application on port 8000

### View Logs

```powershell
docker compose logs -f api
docker compose logs -f db
```

### Stop Services

```powershell
docker compose down
```

## API Endpoints

### Authentication Routes (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Register a new user account |
| `POST` | `/login` | Login and receive JWT tokens |
| `POST` | `/verify-email` | Verify email with code |
| `POST` | `/refresh` | Refresh expired access token |
| `POST` | `/logout` | Logout (invalidate token) |
| `POST` | `/forgot-password` | Request password reset email |
| `POST` | `/reset-password` | Reset password with token |

### Product Routes (`/api/v1/products`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Get all products with pagination |
| `GET` | `/in-stock` | Get only in-stock products |
| `GET` | `/search?q=keyword` | Search products by name/description |
| `GET` | `/{product_id}` | Get product details |

### Shopping Cart Routes (`/api/v1/cart`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Get current cart |
| `POST` | `/items` | Add item to cart |
| `PUT` | `/items/{item_id}` | Update cart item quantity |
| `DELETE` | `/items/{item_id}` | Remove item from cart |
| `DELETE` | `/` | Clear entire cart |

### Order Routes (`/api/v1/orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Get user's orders |
| `GET` | `/{order_id}` | Get order details |
| `POST` | `/` | Create order from cart |
| `POST` | `/{order_id}/cancel` | Cancel an order |

### Admin Routes (`/api/v1/admin`) *Requires Admin Privileges*

#### Products Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/admin/products` | Create new product |
| `PUT` | `/admin/products/{product_id}` | Update product details |
| `PATCH` | `/admin/products/{product_id}/stock` | Update product stock |
| `DELETE` | `/admin/products/{product_id}` | Delete product |

#### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/users` | List all users |
| `GET` | `/admin/users/{user_id}` | Get user details |
| `PATCH` | `/admin/users/{user_id}/role` | Change user role |

#### Order Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/orders` | List all orders |
| `GET` | `/admin/orders/{order_id}` | Get order details |
| `PATCH` | `/admin/orders/{order_id}/status` | Update order status |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | API health status |
| `GET` | `/health/ready` | Readiness probe |

## Authentication

### JWT Token Flow

1. **Register** - Create a new account with email and password
2. **Verify Email** - Use the code sent to email to verify account
3. **Login** - Authenticate with credentials to receive tokens
4. **Access Token** - Use in `Authorization: Bearer <token>` header
5. **Refresh Token** - Use to get new access token when expired

### Example Login Request

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Example Protected Request

```bash
curl -X GET "http://localhost:8000/api/v1/cart/" \
  -H "Authorization: Bearer <your_access_token>"
```

## Database Schema

### Core Models

- **User** - User accounts with roles (user, admin)
- **Product** - Product catalog with pricing and stock
- **ShoppingCart** - User shopping carts
- **CartItem** - Individual items in cart
- **Order** - Placed orders with total and status
- **Payment** - Payment records linked to orders
- **Token** - Refresh tokens for JWT management
- **EmailVerification** - Email verification codes

## Payment Integration

### Stripe Setup

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Get your API keys from the Dashboard
3. Add to `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Payment Methods Supported

- **Card** - Credit/Debit card payments via Stripe
- **Wallet** - Digital wallet payments
- **Cash on Delivery** - COD orders (for local deliveries)

### Example Checkout Flow

1. Add products to cart
2. Create order from cart
3. Initiate payment with Stripe
4. Complete payment
5. Order status updates automatically

## Security Features

- **JWT Authentication** - Stateless token-based auth
- **Password Hashing** - Bcrypt for secure storage
- **Rate Limiting** - Prevent brute force attacks (5 login attempts/minute)
- **CORS** - Configured allowed origins
- **Security Headers** - X-Content-Type-Options, X-Frame-Options, etc.
- **Input Validation** - Pydantic schemas validate all inputs
- **Email Verification** - Verify user email before full access
- **SQL Injection Prevention** - Parameterized queries via SQLAlchemy

## Development Workflows

### Database Migrations

```powershell
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Running Tests

```powershell
# Run pytest
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

### Code Quality

```powershell
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Troubleshooting

### Database Connection Issues

```powershell
# Check if PostgreSQL is running
docker compose ps

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### Migration Errors

```powershell
# Check migration status
alembic current
alembic history

# Stamp database to current migration
alembic stamp head
```

### Redis Connection Issues

```powershell
# Verify Redis is running
redis-cli ping

# If not installed, skip Redis or install locally
pip install redis
```

## Project Structure

```
E-Commerce API/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application setup
│   ├── core/                   # Configuration & utilities
│   │   ├── config.py          # Settings management
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── logging.py         # Logging setup
│   │   ├── rate_limiter.py    # Rate limiting
│   │   ├── redis.py           # Redis client
│   │   └── middleware/        # Custom middleware
│   ├── db/                     # Database layer
│   │   ├── base.py            # SQLAlchemy base classes
│   │   ├── session.py         # Database session
│   │   ├── models/            # ORM models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── seeds/             # Database seeders
│   ├── routers/               # API endpoints
│   │   ├── auth.py            # Authentication routes
│   │   ├── products.py        # Product routes
│   │   ├── cart.py            # Cart routes
│   │   ├── orders.py          # Order routes
│   │   ├── admin/             # Admin routes
│   │   └── health.py          # Health check
│   ├── services/              # Business logic
│   ├── security/              # Auth utilities
│   └── utils/                 # Helper functions
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── main.py                     # Entry point
├── requirements.txt            # Python dependencies
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Container image
└── README.md                   # This file
```

## Requirements

Key dependencies (see [requirements.txt](requirements.txt) for complete list):

- **fastapi** - Web framework
- **sqlalchemy** - ORM
- **alembic** - Migrations
- **pydantic** - Data validation
- **pyjwt** - JWT tokens
- **stripe** - Payment processing
- **redis** - Caching
- **psycopg** - PostgreSQL driver
- **python-multipart** - Form parsing
- **email-validator** - Email validation

## Seed Data

### Production Seed

Minimal dataset suitable for production:

```powershell
python -m app.db.seeds.seed --mode prod
```

Creates:
- 1 admin user
- 10 base products

### Development Seed

Large fake dataset for testing:

```powershell
python -m app.db.seeds.seed --mode dev --users 25 --products 60
```

Creates:
- 25 fake users
- 60 products with realistic data
- Sample orders and carts

## Common Workflows

### Create a New Product

```bash
curl -X POST "http://localhost:8000/api/v1/admin/products" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Name",
    "description": "Product description",
    "price": 99.99,
    "stock_quantity": 100
  }'
```

### Add Item to Cart

```bash
curl -X POST "http://localhost:8000/api/v1/cart/items" \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### Place an Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address": "123 Main St",
    "payment_method": "card"
  }'
```

## Learning Outcomes

By completing this project, you will learn:

- ✅ Building complex APIs with FastAPI
- ✅ Advanced SQLAlchemy ORM patterns
- ✅ JWT authentication and authorization
- ✅ Database design for e-commerce
- ✅ Integrating third-party APIs (Stripe)
- ✅ Building admin panels
- ✅ Implementing shopping cart logic
- ✅ Order and payment workflows
- ✅ Database migrations with Alembic
- ✅ Docker containerization
- ✅ Security best practices
- ✅ Error handling and logging

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your work (`git commit -m 'Add amazing feature'`)
5. Push to your fork (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For questions or issues:

1. Check the [API Documentation](http://localhost:8000/api/v1/docs)
2. Review the code structure in respective router/service files
3. Check Docker logs: `docker compose logs`
4. Review database migrations in `alembic/versions/`

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [Stripe API Reference](https://stripe.com/docs/api)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [JWT Tutorial](https://jwt.io/introduction)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

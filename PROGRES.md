# E-Commerce API Project Plan

## Step 1 - Planning Decisions
- Backend: FastAPI
- Architecture: modular monolith with layered structure (routers, services, db, security)
- Database: PostgreSQL
- ORM: SQLAlchemy 2.0
- Migrations: Alembic
- Auth: JWT access-token authentication
- Async or Sync: async
- API prefix: /api/v1
- Roles: user, admin
- Third-party integrations: Stripe
- Main entities: User, Product, Cart, CartItem, Order, OrderItem
- V1 scope: register and login, protected routes, product list/search/detail, admin product CRUD and inventory management, cart operations, checkout initiation, Stripe payment handling, order creation after successful payment, user order viewing, admin order viewing

## Why These Choices
- FastAPI fits the guide well for a REST API and gives us validation, OpenAPI docs, and a clean async workflow.
- PostgreSQL is the safest choice for relational data like users, carts, orders, and inventory.
- SQLAlchemy plus Alembic is a standard and reliable setup for a Python backend with migrations.
- JWT matches the goal directly and is enough for the first version.
- Async is a good fit because this API will do database I/O and call Stripe.
- A modular monolith keeps the project simple now while still being organized enough for growth.

## Progress Tracker
- [x] Step 1: planning decisions completed
- [x] Step 2: project scaffold created
- [ ] Step 3: database schema design
- [ ] Step 4: models, schemas, and migrations
- [ ] Step 5: authentication and authorization
- [ ] Step 6: products API and admin management
- [ ] Step 7: cart logic
- [ ] Step 8: checkout, Stripe, and orders
- [ ] Step 9: tests, docs, and deployment readiness

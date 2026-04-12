# E-Commerce API — Project Requirements & Goals

> **Source:** [roadmap.sh/projects/ecommerce-api](https://roadmap.sh/projects/ecommerce-api)

---

## Overview

Build a full-featured e-commerce platform API that handles user authentication, product management, shopping carts, and payment processing via Stripe. The project focuses on building a logic-heavy backend with a complex data model and real-world third-party integrations.

---

## Architecture

```
e-commerce app  ──(JWT)──►  Main Backend Service  ──►  Database
                                                   ├──► Users
                                                   ├──► Products
                                                   ├──► Shopping Cart
                                                   ├──► Payments
                                                   └──► Stripe (external)
```

---

## Core Goals

| Goal | Description |
|------|-------------|
| **Authentication** | Secure multi-user access using JWT |
| **CRUD Operations** | Standard create, read, update, delete for all resources |
| **External Integration** | Connect with Stripe as the payment gateway |
| **Complex Data Model** | Handle products, inventory, carts, orders, and payments |

---

## Functional Requirements

### Authentication
- [ ] User sign up (register with email & password)
- [ ] User log in (returns JWT access token)
- [ ] Protected routes requiring valid JWT

### Products
- [ ] View all products (with pagination)
- [ ] Search and filter products
- [ ] Get a single product by ID

### Shopping Cart
- [ ] Add a product to the cart
- [ ] Remove a product from the cart
- [ ] View current cart contents
- [ ] Update item quantities

### Checkout & Payments
- [ ] Initiate checkout from cart
- [ ] Integrate with **Stripe** to process payments
- [ ] Handle payment success and failure responses
- [ ] Create an order record upon successful payment

### Admin Panel
- [ ] Admin-only routes (role-based access)
- [ ] Add / update / delete products
- [ ] Set and update product prices
- [ ] Manage inventory levels
- [ ] View all orders

---

## Suggested Data Models

### User
- `id`, `email`, `password_hash`, `role` (`user` / `admin`), `created_at`

### Product
- `id`, `name`, `description`, `price`, `stock_quantity`, `category`, `created_at`

### Cart
- `id`, `user_id`, `created_at`

### CartItem
- `id`, `cart_id`, `product_id`, `quantity`

### Order
- `id`, `user_id`, `total_amount`, `status`, `stripe_payment_id`, `created_at`

### OrderItem
- `id`, `order_id`, `product_id`, `quantity`, `unit_price`

---

## Tech Stack Suggestions

| Layer | Options |
|-------|---------|
| **Backend Framework** | FastAPI, Express, Django REST |
| **Database** | PostgreSQL + SQLAlchemy / Prisma |
| **Auth** | JWT (access + refresh tokens) |
| **Payment Gateway** | Stripe API |
| **API Testing** | Postman, HTTPie, pytest |
| **Frontend (optional)** | HTML + Jinja2 / EJS templating |

---

## API Endpoints (Rough Plan)

```
POST   /auth/register
POST   /auth/login

GET    /products
GET    /products/:id
POST   /admin/products          (admin only)
PUT    /admin/products/:id      (admin only)
DELETE /admin/products/:id      (admin only)

GET    /cart
POST   /cart/items
PUT    /cart/items/:id
DELETE /cart/items/:id

POST   /checkout
POST   /webhook/stripe          (Stripe payment events)

GET    /orders
GET    /orders/:id
```

---

## Learning Outcomes

- Building authentication flows with JWT (sign-up, login, token validation)
- Designing relational data models for real-world e-commerce logic
- Integrating with a third-party payment API (Stripe)
- Implementing role-based access control (user vs. admin)
- Handling external webhook events (Stripe payment confirmation)
- Structuring a maintainable, logic-heavy REST API

---

## Recommended Build Order

1. Set up project structure and database models
2. Implement JWT auth (register + login)
3. Build product CRUD + admin routes
4. Build cart logic (add, remove, update items)
5. Integrate Stripe checkout session
6. Handle Stripe webhooks to confirm orders
7. (Optional) Build a simple frontend with Jinja2 or similar

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from app.core.rate_limiter import RateLimiter
from app.db.schemas.user_schema import UserRole
from app.db.session import get_db
from app.main import app
from app.security.dependencies import get_current_user


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """Keep dependency overrides isolated between tests."""
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def bypass_rate_limiter(monkeypatch):
    """Avoid Redis in tests by turning rate limiter checks into no-ops."""
    def _allow_request(self, request: Request):
        return None

    monkeypatch.setattr(RateLimiter, "__call__", _allow_request)


@pytest.fixture
def mock_db():
    """Shared fake DB object injected through get_db dependency override."""
    return object()


@pytest.fixture
def client(mock_db):
    """FastAPI test client configured to never open a real DB session."""
    app.dependency_overrides[get_db] = lambda: mock_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()


@pytest.fixture
def make_user():
    """Factory for lightweight auth users used in dependency overrides."""
    def _make(
        role: UserRole = UserRole.customer,
        user_id: int = 1,
        is_active: bool = True,
    ):
        return SimpleNamespace(id=user_id, role=role, is_active=is_active)

    return _make


@pytest.fixture
def override_current_user():
    """Helper to inject authenticated users into endpoint dependencies."""
    def _override(user):
        app.dependency_overrides[get_current_user] = lambda: user

    return _override


@pytest.fixture
def now_utc():
    return datetime.now(timezone.utc)


@pytest.fixture
def product_payload_factory(now_utc):
    """Factory for ProductRead-compatible payloads."""
    def _factory(product_id: int = 1, **overrides):
        payload = {
            "id": product_id,
            "name": "Mechanical Keyboard",
            "description": "Hot-swappable 75% keyboard",
            "price": "129.99",
            "stock_quantity": 20,
            "created_at": now_utc,
            "updated_at": now_utc,
        }
        payload.update(overrides)
        return payload

    return _factory


@pytest.fixture
def cart_payload_factory(now_utc):
    """Factory for ShoppingCartRead-compatible payloads."""
    def _factory(cart_id: int = 1, user_id: int = 1, **overrides):
        payload = {
            "id": cart_id,
            "user_id": user_id,
            "status": "active",
            "created_at": now_utc,
            "updated_at": now_utc,
            "items": [
                {
                    "id": 1,
                    "cart_id": cart_id,
                    "product_id": 1,
                    "quantity": 2,
                    "price_at_time": "129.99",
                    "created_at": now_utc,
                    "updated_at": now_utc,
                }
            ],
        }
        payload.update(overrides)
        return payload

    return _factory


@pytest.fixture
def order_payload_factory(now_utc):
    """Factory for OrderRead-compatible payloads."""
    def _factory(order_id: int = 1, user_id: int = 1, **overrides):
        payload = {
            "id": order_id,
            "user_id": user_id,
            "total_amount": "259.98",
            "status": "pending",
            "created_at": now_utc,
            "updated_at": now_utc,
            "payments": [
                {
                    "id": 1,
                    "order_id": order_id,
                    "amount": "259.98",
                    "method": "card",
                    "status": "pending",
                    "transaction_id": None,
                    "created_at": now_utc,
                    "updated_at": now_utc,
                }
            ],
        }
        payload.update(overrides)
        return payload

    return _factory

"""
Enhanced conftest.py with support for both:
1. Unit tests with mocked database (current approach)
2. Integration tests with real PostgreSQL database

Usage:
- Unit tests: Use mock_db and client fixtures (current)
- Integration tests: Use db_session and async_client fixtures (new)
"""

import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import Request
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.rate_limiter import RateLimiter
from app.db.models.base import Base
from app.db.schemas.user_schema import UserRole
from app.db.session import get_db
from app.main import app
from app.security.dependencies import get_current_user


# ============================================================================
# TEST DATABASE SETUP (for integration tests)
# ============================================================================

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    # Use environment-based URL or default
    import os
    from app.core.config import settings
    
    test_db_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://test_user:test_password@localhost:5434/test_ecommerce_api"
    )
    
    engine = create_async_engine(
        test_db_url,
        echo=False,  # Set to True to see SQL queries in output
        connect_args={"timeout": 10}
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Teardown: drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a fresh database session for each test."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def async_client(db_session) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for integration tests."""
    
    async def override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        app=app,
        base_url="http://test",
        transport=ASGITransport(app=app)
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


# ============================================================================
# UNIT TEST SETUP (mocked database)
# ============================================================================

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
    """FastAPI test client configured to never open a real DB session (UNIT TESTS)."""
    app.dependency_overrides[get_db] = lambda: mock_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()


# ============================================================================
# COMMON FIXTURES
# ============================================================================

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
            "total_price": "0.00",
            "total_items": 0,
            "created_at": now_utc,
            "updated_at": now_utc,
        }
        payload.update(overrides)
        return payload

    return _factory

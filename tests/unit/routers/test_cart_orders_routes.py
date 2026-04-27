from app.db.schemas.user_schema import UserRole
from app.services.cart_service import cart_service
from app.services.order_service import order_service


def test_cart_requires_authentication(client):
    response = client.get("/api/v1/cart/")
    assert response.status_code == 401


def test_get_current_cart_calls_service_with_authenticated_user(
    client,
    monkeypatch,
    cart_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=42))
    expected = cart_payload_factory(cart_id=7, user_id=42)
    captured = {}

    def fake_get_current_cart(db, user_id):
        captured["user_id"] = user_id
        return expected

    monkeypatch.setattr(cart_service, "get_current_cart", fake_get_current_cart)
    response = client.get("/api/v1/cart/")

    assert response.status_code == 200
    assert response.json()["id"] == 7
    assert captured["user_id"] == 42


def test_add_item_to_cart_forwards_payload_and_user_id(
    client,
    monkeypatch,
    cart_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=8))
    expected = cart_payload_factory(cart_id=3, user_id=8)
    captured = {}

    # Assert route-level deserialization produces valid schema object data.
    def fake_add_item(db, user_id, item_data):
        captured["user_id"] = user_id
        captured["product_id"] = item_data.product_id
        captured["quantity"] = item_data.quantity
        return expected

    monkeypatch.setattr(cart_service, "add_item", fake_add_item)
    response = client.post("/api/v1/cart/items", json={"product_id": 1, "quantity": 2})

    assert response.status_code == 200
    assert response.json()["user_id"] == 8
    assert captured == {"user_id": 8, "product_id": 1, "quantity": 2}


def test_update_cart_item_forwards_item_id_and_quantity(
    client,
    monkeypatch,
    cart_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=9))
    expected = cart_payload_factory(cart_id=11, user_id=9)
    captured = {}

    def fake_update_item(db, user_id, item_id, item_data):
        captured["user_id"] = user_id
        captured["item_id"] = item_id
        captured["quantity"] = item_data.quantity
        return expected

    monkeypatch.setattr(cart_service, "update_item", fake_update_item)
    response = client.put("/api/v1/cart/items/77", json={"quantity": 5})

    assert response.status_code == 200
    assert captured == {"user_id": 9, "item_id": 77, "quantity": 5}


def test_remove_cart_item_forwards_path_item_id(
    client,
    monkeypatch,
    cart_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=10))
    expected = cart_payload_factory(cart_id=1, user_id=10)
    captured = {}

    def fake_remove_item(db, user_id, item_id):
        captured["user_id"] = user_id
        captured["item_id"] = item_id
        return expected

    monkeypatch.setattr(cart_service, "remove_item", fake_remove_item)
    response = client.delete("/api/v1/cart/items/99")

    assert response.status_code == 200
    assert captured == {"user_id": 10, "item_id": 99}


def test_clear_current_cart_calls_service_with_user_id(
    client,
    monkeypatch,
    cart_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=12))
    expected = cart_payload_factory(cart_id=4, user_id=12, items=[])
    captured = {}

    def fake_clear_cart(db, user_id):
        captured["user_id"] = user_id
        return expected

    monkeypatch.setattr(cart_service, "clear_current_cart", fake_clear_cart)
    response = client.delete("/api/v1/cart/items")

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert captured["user_id"] == 12


def test_orders_requires_authentication(client):
    response = client.get("/api/v1/orders/")
    assert response.status_code == 401


def test_checkout_calls_service_and_returns_created_order(
    client,
    monkeypatch,
    order_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=5))
    expected = order_payload_factory(order_id=15, user_id=5)
    captured = {}

    def fake_checkout(db, user_id, data):
        captured["user_id"] = user_id
        captured["cart_id"] = data.cart_id
        captured["payment_method"] = data.payment_method.value
        return expected

    monkeypatch.setattr(order_service, "checkout", fake_checkout)
    response = client.post("/api/v1/orders/checkout", json={"cart_id": 3, "payment_method": "card"})

    assert response.status_code == 201
    assert response.json()["id"] == 15
    assert captured == {"user_id": 5, "cart_id": 3, "payment_method": "card"}


def test_get_my_orders_forwards_pagination(
    client,
    monkeypatch,
    order_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=23))
    expected = [order_payload_factory(order_id=1, user_id=23)]
    captured = {}

    def fake_get_orders_for_user(db, user_id, skip, limit):
        captured["user_id"] = user_id
        captured["skip"] = skip
        captured["limit"] = limit
        return expected

    monkeypatch.setattr(order_service, "get_orders_for_user", fake_get_orders_for_user)
    response = client.get("/api/v1/orders/?skip=2&limit=3")

    assert response.status_code == 200
    assert response.json()[0]["user_id"] == 23
    assert captured == {"user_id": 23, "skip": 2, "limit": 3}


def test_get_order_for_user_forwards_order_id_and_user_id(
    client,
    monkeypatch,
    order_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=33))
    expected = order_payload_factory(order_id=44, user_id=33)
    captured = {}

    def fake_get_order_for_user(db, order_id, user_id):
        captured["order_id"] = order_id
        captured["user_id"] = user_id
        return expected

    monkeypatch.setattr(order_service, "get_order_for_user", fake_get_order_for_user)
    response = client.get("/api/v1/orders/44")

    assert response.status_code == 200
    assert response.json()["id"] == 44
    assert captured == {"order_id": 44, "user_id": 33}

from app.db.schemas.user_schema import UserRole
from app.services.order_service import order_service
from app.services.product_service import product_service


def test_admin_create_product_calls_service_and_returns_created_product(
    client,
    monkeypatch,
    product_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.staff, user_id=2))
    expected = product_payload_factory(product_id=501, name="Laptop")
    captured = {}

    def fake_create_product(db, product_data):
        captured["name"] = product_data.name
        captured["price"] = str(product_data.price)
        return expected

    monkeypatch.setattr(product_service, "create_product", fake_create_product)
    response = client.post(
        "/api/v1/admin/products/",
        json={
            "name": "Laptop",
            "description": "Business laptop",
            "price": "1199.99",
            "stock_quantity": 15,
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 501
    assert captured == {"name": "Laptop", "price": "1199.99"}


def test_admin_update_product_returns_404_when_service_returns_none(
    client,
    monkeypatch,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.staff, user_id=2))
    monkeypatch.setattr(product_service, "update_product", lambda db, product_id, product_data: None)

    response = client.put("/api/v1/admin/products/999", json={"name": "Updated Name"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_admin_delete_product_returns_404_when_service_returns_false(
    client,
    monkeypatch,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.staff, user_id=2))
    monkeypatch.setattr(product_service, "delete_product", lambda db, product_id: False)

    response = client.delete("/api/v1/admin/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_admin_list_orders_forwards_pagination(
    client,
    monkeypatch,
    order_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.staff, user_id=2))
    expected = [order_payload_factory(order_id=601, user_id=40)]
    captured = {}

    def fake_get_all_orders(db, skip, limit):
        captured["skip"] = skip
        captured["limit"] = limit
        return expected

    monkeypatch.setattr(order_service, "get_all_orders", fake_get_all_orders)
    response = client.get("/api/v1/admin/orders/?skip=3&limit=5")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 601
    assert captured == {"skip": 3, "limit": 5}


def test_admin_get_single_order_calls_service(
    client,
    monkeypatch,
    order_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.staff, user_id=2))
    expected = order_payload_factory(order_id=777, user_id=42)
    captured = {}

    def fake_get_order_admin(db, order_id):
        captured["order_id"] = order_id
        return expected

    monkeypatch.setattr(order_service, "get_order_admin", fake_get_order_admin)
    response = client.get("/api/v1/admin/orders/777")

    assert response.status_code == 200
    assert response.json()["id"] == 777
    assert captured["order_id"] == 777


def test_admin_update_order_calls_service_and_returns_updated_payload(
    client,
    monkeypatch,
    order_payload_factory,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.staff, user_id=2))
    expected = order_payload_factory(order_id=901, status="paid")
    captured = {}

    def fake_update_order(db, order_id, data):
        captured["order_id"] = order_id
        captured["status"] = data.status.value if data.status else None
        return expected

    monkeypatch.setattr(order_service, "update_order", fake_update_order)
    response = client.put("/api/v1/admin/orders/901", json={"status": "paid"})

    assert response.status_code == 200
    assert response.json()["status"] == "paid"
    assert captured == {"order_id": 901, "status": "paid"}

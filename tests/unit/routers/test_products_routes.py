from app.services.product_service import product_service


def test_get_products_returns_payload_and_uses_pagination(
    client,
    mock_db,
    monkeypatch,
    product_payload_factory,
):
    expected = [
        product_payload_factory(product_id=1, name="Keyboard"),
        product_payload_factory(product_id=2, name="Mouse"),
    ]
    captured = {}

    # Capture service args to ensure query params are forwarded correctly.
    def fake_get_products(db, skip, limit):
        captured["db"] = db
        captured["skip"] = skip
        captured["limit"] = limit
        return expected

    monkeypatch.setattr(product_service, "get_products", fake_get_products)
    response = client.get("/api/v1/products/?skip=5&limit=2")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [1, 2]
    assert captured == {"db": mock_db, "skip": 5, "limit": 2}


def test_get_products_in_stock_returns_payload(client, monkeypatch, product_payload_factory):
    expected = [product_payload_factory(product_id=10, stock_quantity=3)]
    monkeypatch.setattr(product_service, "get_products_in_stock", lambda db, skip, limit: expected)

    response = client.get("/api/v1/products/in-stock?skip=0&limit=10")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 10


def test_search_products_requires_query_param(client):
    # Missing mandatory `q` parameter should fail at request validation level.
    response = client.get("/api/v1/products/search")
    assert response.status_code == 422


def test_search_products_forwards_query_and_pagination(
    client,
    mock_db,
    monkeypatch,
    product_payload_factory,
):
    expected = [product_payload_factory(product_id=20, name="Monitor")]
    captured = {}

    def fake_search_products(db, query, skip, limit):
        captured["db"] = db
        captured["query"] = query
        captured["skip"] = skip
        captured["limit"] = limit
        return expected

    monkeypatch.setattr(product_service, "search_products", fake_search_products)
    response = client.get("/api/v1/products/search?q=monitor&skip=1&limit=3")

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Monitor"
    assert captured == {"db": mock_db, "query": "monitor", "skip": 1, "limit": 3}


def test_get_products_by_price_range_rejects_invalid_bounds(client):
    # Business rule: min_price must be strictly less than max_price.
    response = client.get("/api/v1/products/price-range?min_price=100&max_price=100")
    assert response.status_code == 400
    assert response.json()["detail"] == "min_price must be less than max_price"


def test_get_products_by_price_range_calls_service_with_float_values(
    client,
    mock_db,
    monkeypatch,
    product_payload_factory,
):
    expected = [product_payload_factory(product_id=30, price="79.99")]
    captured = {}

    def fake_price_range(db, min_price, max_price, skip, limit):
        captured["db"] = db
        captured["min_price"] = min_price
        captured["max_price"] = max_price
        captured["skip"] = skip
        captured["limit"] = limit
        return expected

    monkeypatch.setattr(product_service, "get_products_by_price_range", fake_price_range)
    response = client.get("/api/v1/products/price-range?min_price=10.50&max_price=99.90&skip=2&limit=4")

    assert response.status_code == 200
    assert response.json()[0]["id"] == 30
    assert captured == {
        "db": mock_db,
        "min_price": 10.5,
        "max_price": 99.9,
        "skip": 2,
        "limit": 4,
    }


def test_get_product_returns_404_when_service_returns_none(client, monkeypatch):
    monkeypatch.setattr(product_service, "get_product_by_id", lambda db, product_id: None)

    response = client.get("/api/v1/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

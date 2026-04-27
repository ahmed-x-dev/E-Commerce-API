def test_root_endpoint_returns_running_message(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "is running" in response.json()["message"]


def test_security_headers_middleware_adds_expected_headers(client):
    # Ensure middleware remains active for every response.
    response = client.get("/")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert "max-age=31536000" in response.headers["strict-transport-security"]


def test_health_endpoint_returns_ok_when_database_check_succeeds(client, monkeypatch):
    monkeypatch.setattr("app.routers.health.check_db_connection", lambda: True)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_health_endpoint_returns_degraded_when_database_check_fails(client, monkeypatch):
    monkeypatch.setattr("app.routers.health.check_db_connection", lambda: False)

    response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}

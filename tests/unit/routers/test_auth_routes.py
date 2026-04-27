from app.db.schemas.user_schema import UserRole
from app.services.auth_service import AuthService


def test_register_returns_created_user(client, monkeypatch, now_utc):
    expected_user = {
        "id": 101,
        "name": "Alice",
        "email": "alice@example.com",
        "created_at": now_utc,
        "updated_at": now_utc,
    }
    captured = {}

    # Service layer is mocked to keep this as a pure router behavior test.
    def fake_register(db, data):
        captured["email"] = data.email
        captured["name"] = data.name
        return expected_user

    monkeypatch.setattr(AuthService, "register", fake_register)
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "name": "Alice", "password": "StrongPass123"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "alice@example.com"
    assert captured == {"email": "alice@example.com", "name": "Alice"}


def test_login_returns_access_token_and_sets_refresh_cookie(client, monkeypatch):
    monkeypatch.setattr(AuthService, "login", lambda db, data: ("access-token", "refresh-token"))

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 200
    assert response.json() == {"access_token": "access-token", "token_type": "bearer"}
    assert "refresh_token=refresh-token" in response.headers["set-cookie"]


def test_refresh_requires_refresh_cookie(client):
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token missing"


def test_refresh_rotates_token_and_sets_new_cookie(client, monkeypatch):
    captured = {}

    def fake_refresh(db, refresh_token):
        captured["old_refresh"] = refresh_token
        return "new-access-token", "new-refresh-token"

    monkeypatch.setattr(AuthService, "refresh", fake_refresh)
    client.cookies.set("refresh_token", "old-refresh-token")
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    assert response.json()["access_token"] == "new-access-token"
    assert captured["old_refresh"] == "old-refresh-token"
    assert "refresh_token=new-refresh-token" in response.headers["set-cookie"]


def test_logout_with_cookie_revokes_token_and_clears_cookie(
    client,
    monkeypatch,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=55))
    captured = {}

    def fake_logout(db, refresh_token):
        captured["refresh_token"] = refresh_token

    monkeypatch.setattr(AuthService, "logout", fake_logout)
    client.cookies.set("refresh_token", "refresh-to-revoke")
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out successfully"}
    assert captured["refresh_token"] == "refresh-to-revoke"
    assert "refresh_token=" in response.headers["set-cookie"]


def test_logout_without_cookie_still_returns_200(
    client,
    monkeypatch,
    make_user,
    override_current_user,
):
    override_current_user(make_user(role=UserRole.customer, user_id=1))
    called = {"value": False}

    # No refresh cookie means service should not be called.
    def fake_logout(db, refresh_token):
        called["value"] = True

    monkeypatch.setattr(AuthService, "logout", fake_logout)
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    assert called["value"] is False


def test_verify_email_calls_service_and_returns_success_message(client, monkeypatch):
    captured = {}

    def fake_verify_email(db, data):
        captured["email"] = data.email
        captured["code"] = data.code

    monkeypatch.setattr(AuthService, "verify_email", fake_verify_email)
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "alice@example.com", "code": "123456"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Email verified successfully"}
    assert captured == {"email": "alice@example.com", "code": "123456"}


def test_request_password_reset_calls_service(client, monkeypatch):
    captured = {}

    def fake_forgot_password(db, email):
        captured["email"] = email

    monkeypatch.setattr(AuthService, "forgot_password", fake_forgot_password)
    response = client.post("/api/v1/auth/request-password-reset", json={"email": "bob@example.com"})

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset email sent if the email is registered"}
    assert captured["email"] == "bob@example.com"


def test_reset_password_calls_service_with_expected_arguments(client, monkeypatch):
    captured = {}

    def fake_reset_password(db, email, code, new_password):
        captured["email"] = email
        captured["code"] = code
        captured["new_password"] = new_password

    monkeypatch.setattr(AuthService, "reset_password", fake_reset_password)
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": "bob@example.com",
            "code": "654321",
            "new_password": "NewStrongPass123",
        },
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Password reset successfully"}
    assert captured == {
        "email": "bob@example.com",
        "code": "654321",
        "new_password": "NewStrongPass123",
    }

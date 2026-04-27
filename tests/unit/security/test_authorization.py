from app.db.schemas.user_schema import UserRole


def test_staff_ping_without_token_returns_401(client):
    # No auth header should fail on admin router dependency.
    response = client.get("/api/v1/admin/users/staff_ping")
    assert response.status_code == 401


def test_staff_ping_with_customer_role_returns_403(client, make_user, override_current_user):
    # Customer role is authenticated but lacks required staff/admin role.
    override_current_user(make_user(role=UserRole.customer))
    response = client.get("/api/v1/admin/users/staff_ping")
    assert response.status_code == 403


def test_staff_ping_with_staff_role_returns_200(client, make_user, override_current_user):
    # Staff role satisfies router-level `get_staff_user` dependency.
    override_current_user(make_user(role=UserRole.staff))
    response = client.get("/api/v1/admin/users/staff_ping")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_admin_ping_with_staff_role_returns_403(client, make_user, override_current_user):
    # Endpoint-level `get_admin_user` should reject staff accounts.
    override_current_user(make_user(role=UserRole.staff))
    response = client.get("/api/v1/admin/users/admin_ping")
    assert response.status_code == 403


def test_admin_ping_with_admin_role_returns_200(client, make_user, override_current_user):
    # Full admin role can pass both router-level and endpoint-level checks.
    override_current_user(make_user(role=UserRole.admin))
    response = client.get("/api/v1/admin/users/admin_ping")
    assert response.status_code == 200
    assert response.json() == {"ok": True}

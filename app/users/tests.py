import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="TestPass123!",
    )


@pytest.mark.django_db
class TestHealthEndpoint:
    def test_health_returns_ok(self, api_client):
        resp = api_client.get("/health/")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        u = User.objects.create_user(
            email="u@test.com", username="u1", password="pass1234"
        )
        assert u.email == "u@test.com"
        assert u.check_password("pass1234")
        assert not u.is_staff
        assert not u.is_superuser

    def test_create_superuser(self):
        u = User.objects.create_superuser(
            email="admin@test.com", username="admin", password="pass1234"
        )
        assert u.is_staff
        assert u.is_superuser

    def test_email_required(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email="", username="x", password="p")

    def test_str(self, user):
        assert str(user) == "test@example.com"

    def test_full_name(self, user):
        user.first_name = "John"
        user.last_name = "Doe"
        assert user.full_name == "John Doe"


@pytest.mark.django_db
class TestAuthEndpoints:
    def test_register(self, api_client):
        resp = api_client.post("/api/v1/auth/register/", {
            "email": "new@test.com",
            "username": "newuser",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        assert resp.status_code == 201
        assert User.objects.filter(email="new@test.com").exists()

    def test_register_password_mismatch(self, api_client):
        resp = api_client.post("/api/v1/auth/register/", {
            "email": "new@test.com",
            "username": "newuser",
            "password": "StrongPass1!",
            "password2": "DifferentPass1!",
        })
        assert resp.status_code == 400

    def test_login(self, api_client, user):
        resp = api_client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        assert "access" in resp.json()
        assert "refresh" in resp.json()

    def test_login_wrong_password(self, api_client, user):
        resp = api_client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_me_unauthenticated(self, api_client):
        resp = api_client.get("/api/v1/users/me/")
        assert resp.status_code == 401

    def test_me_authenticated(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/v1/users/me/")
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

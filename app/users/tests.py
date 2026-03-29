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

    def test_login_returns_user_data(self, api_client, user):
        resp = api_client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        assert resp.status_code == 200
        assert resp.json()["user"]["email"] == "test@example.com"

    def test_register_duplicate_email(self, api_client, user):
        resp = api_client.post("/api/v1/auth/register/", {
            "email": "test@example.com",
            "username": "different",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        assert resp.status_code == 400

    def test_register_duplicate_username(self, api_client, user):
        resp = api_client.post("/api/v1/auth/register/", {
            "email": "other@test.com",
            "username": "testuser",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestLogout:
    def test_logout_blacklists_token(self, api_client, user):
        login = api_client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        refresh = login.json()["refresh"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")
        resp = api_client.post("/api/v1/auth/logout/", {"refresh": refresh})
        assert resp.status_code == 205

    def test_logout_invalid_token(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.post("/api/v1/auth/logout/", {"refresh": "invalidtoken"})
        assert resp.status_code == 400

    def test_logout_missing_token(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.post("/api/v1/auth/logout/", {})
        assert resp.status_code == 400

    def test_logout_same_token_twice(self, api_client, user):
        login = api_client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        refresh = login.json()["refresh"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")
        api_client.post("/api/v1/auth/logout/", {"refresh": refresh})
        resp = api_client.post("/api/v1/auth/logout/", {"refresh": refresh})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestChangePassword:
    def test_change_password(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.put("/api/v1/users/me/change-password/", {
            "old_password": "TestPass123!",
            "new_password": "NewStrong1!",
            "new_password2": "NewStrong1!",
        })
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.check_password("NewStrong1!")

    def test_change_password_wrong_old(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.put("/api/v1/users/me/change-password/", {
            "old_password": "WrongPass1!",
            "new_password": "NewStrong1!",
            "new_password2": "NewStrong1!",
        })
        assert resp.status_code == 400

    def test_change_password_mismatch(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.put("/api/v1/users/me/change-password/", {
            "old_password": "TestPass123!",
            "new_password": "NewStrong1!",
            "new_password2": "Different1!",
        })
        assert resp.status_code == 400

    def test_change_password_unauthenticated(self, api_client):
        resp = api_client.put("/api/v1/users/me/change-password/", {
            "old_password": "TestPass123!",
            "new_password": "NewStrong1!",
            "new_password2": "NewStrong1!",
        })
        assert resp.status_code == 401

    def test_change_password_too_simple(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.put("/api/v1/users/me/change-password/", {
            "old_password": "TestPass123!",
            "new_password": "123",
            "new_password2": "123",
        })
        assert resp.status_code == 400


@pytest.mark.django_db
class TestUpdateProfile:
    def test_patch_profile(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.patch("/api/v1/users/me/", {
            "first_name": "John",
            "last_name": "Doe",
        })
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_update_bio(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.patch("/api/v1/users/me/", {"bio": "Hello world"})
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.bio == "Hello world"

    def test_update_username(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.patch("/api/v1/users/me/", {"username": "newname"})
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.username == "newname"

    def test_update_profile_unauthenticated(self, api_client):
        resp = api_client.patch("/api/v1/users/me/", {"bio": "test"})
        assert resp.status_code == 401

    def test_cannot_update_email(self, api_client, user):
        api_client.force_authenticate(user=user)
        resp = api_client.patch("/api/v1/users/me/", {"email": "hacked@test.com"})
        assert resp.status_code == 200
        user.refresh_from_db()
        assert user.email == "test@example.com"

    def test_me_returns_full_name(self, api_client, user):
        user.first_name = "Jane"
        user.last_name = "Smith"
        user.save()
        api_client.force_authenticate(user=user)
        resp = api_client.get("/api/v1/users/me/")
        assert resp.json()["full_name"] == "Jane Smith"


@pytest.mark.django_db
class TestTokenRefresh:
    def test_refresh_returns_new_access(self, api_client, user):
        login = api_client.post("/api/v1/auth/login/", {
            "email": "test@example.com",
            "password": "TestPass123!",
        })
        refresh = login.json()["refresh"]
        resp = api_client.post("/api/v1/auth/token/refresh/", {"refresh": refresh})
        assert resp.status_code == 200
        assert "access" in resp.json()

    def test_refresh_invalid_token(self, api_client):
        resp = api_client.post("/api/v1/auth/token/refresh/", {"refresh": "garbage"})
        assert resp.status_code == 401

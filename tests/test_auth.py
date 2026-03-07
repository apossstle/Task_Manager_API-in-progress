"""
Тесты аутентификации: POST /users/register, POST /users/login
"""
import pytest


class TestRegister:

    def test_register_success(self, client):
        resp = client.post("/users/register", json={"email": "a@a.com", "password": "pass123"})
        assert resp.status_code == 201

    def test_register_returns_user_fields(self, client):
        data = client.post("/users/register", json={"email": "a@a.com", "password": "pass123"}).json()
        assert "id" in data
        assert "email" in data
        assert "created_at" in data
        assert "password" not in data           # пароль никогда не должен возвращаться
        assert "hashed_password" not in data

    def test_register_duplicate_email_returns_400(self, client):
        payload = {"email": "dup@a.com", "password": "pass123"}
        client.post("/users/register", json=payload)
        resp = client.post("/users/register", json=payload)
        assert resp.status_code == 400

    def test_register_invalid_email_returns_422(self, client):
        resp = client.post("/users/register", json={"email": "not-an-email", "password": "pass123"})
        assert resp.status_code == 422

    def test_register_missing_password_returns_422(self, client):
        resp = client.post("/users/register", json={"email": "a@a.com"})
        assert resp.status_code == 422

    def test_register_short_password_returns_422(self, client):
        """Пароль меньше 6 символов — не должен приниматься."""
        resp = client.post("/users/register", json={"email": "a@a.com", "password": "123"})
        assert resp.status_code == 422

    @pytest.mark.parametrize("email", ["", "   ", "@nodomain", "nodomain@"])
    def test_register_invalid_emails(self, client, email):
        resp = client.post("/users/register", json={"email": email, "password": "pass123"})
        assert resp.status_code == 422


class TestLogin:

    def test_login_success_returns_token(self, client, registered_user):
        resp = client.post("/users/login", data={"username": "test@example.com", "password": "password123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client, registered_user):
        resp = client.post("/users/login", data={"username": "test@example.com", "password": "wrongpass"})
        assert resp.status_code == 401

    def test_login_nonexistent_user_returns_401(self, client):
        resp = client.post("/users/login", data={"username": "ghost@example.com", "password": "pass123"})
        assert resp.status_code == 401

    def test_login_missing_credentials_returns_422(self, client):
        resp = client.post("/users/login", data={})
        assert resp.status_code == 422

    def test_token_is_non_empty_string(self, client, registered_user):
        resp = client.post("/users/login", data={"username": "test@example.com", "password": "password123"})
        token = resp.json()["access_token"]
        assert isinstance(token, str) and len(token) > 10

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_temp.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

USER_EMAIL = "test@example.com"
USER_PASSWORD = "password123"
USER2_EMAIL = "other@example.com"
USER2_PASSWORD = "password456"


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    db = TestingSessionLocal()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    resp = client.post("/users/register", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def auth_token(client, registered_user):
    resp = client.post("/users/login", data={"username": USER_EMAIL, "password": USER_PASSWORD})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def second_user_headers(client):
    client.post("/users/register", json={"email": USER2_EMAIL, "password": USER2_PASSWORD})
    resp = client.post("/users/login", data={"username": USER2_EMAIL, "password": USER2_PASSWORD})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def created_task(client, auth_headers):
    resp = client.post("/tasks", json={
        "title": "Тестовая задача",
        "description": "Описание для теста",
        "priority": 2,
    }, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()

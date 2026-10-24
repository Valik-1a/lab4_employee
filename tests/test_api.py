import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_employee.db")

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)
ADMIN = {"X-API-Key": "admin-demo-key"}
READER = {"X-API-Key": "read-demo-key"}


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_unauthorized() -> None:
    response = client.get("/employees")
    assert response.status_code == 401


def test_report_is_small() -> None:
    response = client.get("/report")
    assert response.status_code == 200
    assert len(response.content) < 14 * 1024


def test_invalid_email_rejected() -> None:
    response = client.post(
        "/employees",
        headers=ADMIN,
        json={
            "full_name": "Тест Працівник",
            "email": "wrong-email",
            "phone": "+380501234567",
            "position": "Тестувальник",
            "salary": 20000,
            "department_id": 1,
        },
    )
    assert response.status_code == 422


from datetime import datetime, timezone
from app.main import app
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db


def sample_appointment():
    return {
        "patient_name": "Test Patient",
        "appointment_at": datetime(
            2026, 11, 20, 14, 0, tzinfo=timezone.utc
        ).isoformat(),
        "notes": "Automated test appointment",
    }


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "Physio API"


def test_liveness(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness(client):
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["database"] == "connected"


def test_create_appointment(client):
    response = client.post(
        "/api/v1/appointments",
        json=sample_appointment(),
    )

    assert response.status_code == 201

    data = response.json()
    assert data["patient_name"] == "Test Patient"
    assert data["status"] == "scheduled"
    assert data["id"] is not None


def test_list_appointments(client):
    client.post(
        "/api/v1/appointments",
        json=sample_appointment(),
    )

    response = client.get("/api/v1/appointments")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_appointment(client):
    create_response = client.post(
        "/api/v1/appointments",
        json=sample_appointment(),
    )

    appointment_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/appointments/{appointment_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == appointment_id


def test_get_nonexistent_appointment(client):
    response = client.get("/api/v1/appointments/999999")

    assert response.status_code == 404


def test_delete_appointment(client):
    create_response = client.post(
        "/api/v1/appointments",
        json=sample_appointment(),
    )

    appointment_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/api/v1/appointments/{appointment_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/api/v1/appointments/{appointment_id}"
    )

    assert get_response.status_code == 404


def test_invalid_appointment(client):
    invalid_data = {
        "patient_name": "A",
        "appointment_at": "not-a-date",
    }

    response = client.post(
        "/api/v1/appointments",
        json=invalid_data,
    )

    assert response.status_code == 422


def test_readiness_database_failure(client):
    class BrokenDB:
        def execute(self, statement):
            raise SQLAlchemyError("Simulated database failure")

        def close(self):
            pass

    def override_broken_db():
        yield BrokenDB()

    app = client.app
    app.dependency_overrides[get_db] = override_broken_db

    response = client.get("/health/ready")

    assert response.status_code == 503

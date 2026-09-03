from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.database.models import Customer, Policy


client = TestClient(app)


def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_POLICY_API",
        name="Policy API Test Customer",
        email="policytest@example.com",
        phone="8888888888",
    )

    policy = Policy(
        policy_id="POL_TEST_POLICY_API",
        customer_id="CUS_TEST_POLICY_API",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS12EF9012",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000.0,
        coverage_amount=1000000.0,
        status="ACTIVE",
    )

    db.add(customer)
    db.commit()

    db.add(policy)
    db.commit()


def test_policy_active_success(db):
    create_test_data(db)

    response = client.get(
        "/policies/POL_TEST_POLICY_API/active"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["policy_id"] == "POL_TEST_POLICY_API"
    assert data["active"] is True


def test_policy_not_found():
    response = client.get(
        "/policies/POL_DOES_NOT_EXIST/active"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Policy with ID POL_DOES_NOT_EXIST not found."
    )


def test_incident_coverage_success(db):
    create_test_data(db)

    response = client.get(
        "/policies/POL_TEST_POLICY_API/coverage",
        params={
            "incident_date": "2026-08-15"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["policy_id"] == "POL_TEST_POLICY_API"
    assert data["incident_date"] == "2026-08-15"
    assert data["covered"] is True
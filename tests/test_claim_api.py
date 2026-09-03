from datetime import date

from fastapi.testclient import TestClient

from app.main import app
from app.database.models import Customer, Policy, Claim, Document


client = TestClient(app)


def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_API",
        name="API Test Customer",
        email="apitest@example.com",
        phone="9999999999",
    )

    policy = Policy(
        policy_id="POL_TEST_API",
        customer_id="CUS_TEST_API",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS10AB1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000.0,
        coverage_amount=1000000.0,
        status="ACTIVE",
    )

    claim = Claim(
        claim_id="CLM_TEST_API",
        customer_id="CUS_TEST_API",
        policy_id="POL_TEST_API",
        incident_date=date(2026, 8, 15),
        claim_date=date(2026, 8, 20),
        claim_type="ACCIDENT",
        description="Vehicle accident during testing",
        claim_amount=150000.0,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    document = Document(
        document_id="DOC_TEST_API",
        claim_id="CLM_TEST_API",
        document_type="ACCIDENT_PHOTO",
        file_name="accident.jpg",
        storage_path="documents/CLM_TEST_API/accident.jpg",
        verification_status="PENDING",
    )

    # Insert records in foreign-key dependency order
    db.add(customer)
    db.commit()

    db.add(policy)
    db.commit()

    db.add(claim)
    db.commit()

    db.add(document)
    db.commit()


def test_get_claim_success(db):
    create_test_data(db)

    response = client.get("/claims/CLM_TEST_API")

    assert response.status_code == 200

    data = response.json()

    assert data["claim_id"] == "CLM_TEST_API"
    assert data["customer_id"] == "CUS_TEST_API"
    assert data["policy_id"] == "POL_TEST_API"
    assert data["status"] == "SUBMITTED"


def test_get_claim_not_found():
    response = client.get("/claims/CLM_DOES_NOT_EXIST")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Claim with ID CLM_DOES_NOT_EXIST not found."
    )


def test_validate_claim_success(db):
    create_test_data(db)

    response = client.get(
        "/claims/CLM_TEST_API/validate"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["claim_id"] == "CLM_TEST_API"
    assert data["valid"] is True
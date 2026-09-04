from fastapi.testclient import TestClient

from app.main import app
from app.database.models import Customer, Policy, Claim, Document


client = TestClient(app)


def create_test_data(db):
    customer = Customer(
        customer_id="CUS_TEST_DOCUMENT_API",
        name="Document API Test Customer",
        email="document.api@example.com",
        phone="6666666666",
    )

    policy = Policy(
        policy_id="POL_TEST_DOCUMENT_API",
        customer_id="CUS_TEST_DOCUMENT_API",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS13GH3456",
        start_date="2026-01-01",
        end_date="2026-12-31",
        premium=25000.0,
        coverage_amount=1000000.0,
        status="ACTIVE",
    )

    claim = Claim(
        claim_id="CLM_TEST_DOCUMENT_API",
        customer_id="CUS_TEST_DOCUMENT_API",
        policy_id="POL_TEST_DOCUMENT_API",
        incident_date="2026-08-15",
        claim_date="2026-08-20",
        claim_type="ACCIDENT",
        description="Vehicle accident for document API testing",
        claim_amount=150000.0,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    document = Document(
        document_id="DOC_TEST_DOCUMENT_API",
        claim_id="CLM_TEST_DOCUMENT_API",
        document_type="ACCIDENT_PHOTO",
        file_name="accident.jpg",
        storage_path="documents/CLM_TEST_DOCUMENT_API/accident.jpg",
        verification_status="PENDING",
    )

    # Foreign-key dependency order
    db.add(customer)
    db.commit()

    db.add(policy)
    db.commit()

    db.add(claim)
    db.commit()

    db.add(document)
    db.commit()


def test_get_document_success(db):
    create_test_data(db)

    response = client.get(
        "/documents/DOC_TEST_DOCUMENT_API"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == "DOC_TEST_DOCUMENT_API"
    assert data["claim_id"] == "CLM_TEST_DOCUMENT_API"
    assert data["document_type"] == "ACCIDENT_PHOTO"
    assert data["verification_status"] == "PENDING"


def test_get_document_not_found():
    response = client.get(
        "/documents/DOC_DOES_NOT_EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == (
        "Document with ID DOC_DOES_NOT_EXIST not found."
    )


def test_get_documents_by_claim(db):
    create_test_data(db)

    response = client.get(
        "/documents/claim/CLM_TEST_DOCUMENT_API"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["document_id"] == "DOC_TEST_DOCUMENT_API"
    assert data[0]["claim_id"] == "CLM_TEST_DOCUMENT_API"
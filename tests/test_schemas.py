import pytest
from pydantic import ValidationError

from app.models.schemas import (
    Customer,
    Policy,
    Claim,
    Document,
    PolicyType,
    ClaimType,
    ClaimStatus,
)


def test_customer_creation():
    customer = Customer(
        customer_id="CUS001",
        name="Rahul Sharma",
        email="rahul@example.com",
        phone="9876543210"
    )

    assert customer.customer_id == "CUS001"
    assert customer.name == "Rahul Sharma"
    assert customer.email == "rahul@example.com"
    assert customer.phone == "9876543210"


def test_policy_creation():
    policy = Policy(
        policy_id="POL001",
        customer_id="CUS001",
        policy_type=PolicyType.COMPREHENSIVE,
        vehicle_number="TS09AB1234",
        start_date="2026-01-01",
        end_date="2026-12-31",
        premium=25000,
        coverage_amount=800000,
        status="ACTIVE"
    )

    assert policy.policy_id == "POL001"
    assert policy.customer_id == "CUS001"
    assert policy.policy_type == PolicyType.COMPREHENSIVE
    assert policy.vehicle_number == "TS09AB1234"
    assert policy.premium == 25000
    assert policy.coverage_amount == 800000
    assert policy.status == "ACTIVE"


def test_claim_creation():
    claim = Claim(
        claim_id="CLM001",
        customer_id="CUS001",
        policy_id="POL001",
        incident_date="2026-08-20",
        claim_date="2026-08-21",
        claim_type=ClaimType.ACCIDENT,
        description="Vehicle damaged in road accident",
        claim_amount=145000,
        status=ClaimStatus.SUBMITTED
    )

    assert claim.claim_id == "CLM001"
    assert claim.customer_id == "CUS001"
    assert claim.policy_id == "POL001"
    assert claim.claim_type == ClaimType.ACCIDENT
    assert claim.claim_amount == 145000
    assert claim.status == ClaimStatus.SUBMITTED
    assert claim.fraud_score is None
    assert claim.decision is None


def test_document_creation():
    document = Document(
        document_id="DOC001",
        claim_id="CLM001",
        document_type="POLICE_REPORT",
        file_name="police_report.pdf",
        storage_path="/documents/CLM001/police_report.pdf",
        verification_status="PENDING"
    )

    assert document.document_id == "DOC001"
    assert document.claim_id == "CLM001"
    assert document.document_type == "POLICE_REPORT"
    assert document.file_name == "police_report.pdf"
    assert document.verification_status == "PENDING"


def test_invalid_customer_email():
    with pytest.raises(ValidationError):
        Customer(
            customer_id="CUS001",
            name="Rahul Sharma",
            email="invalid-email",
            phone="9876543210"
        )
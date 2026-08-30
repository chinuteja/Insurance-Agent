from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository


def test_create_and_get_claim(db):
    customer = Customer(
        customer_id="CUS_CLAIM_TEST",
        name="Claim Test Customer",
        email="claimtest@example.com",
        phone="7777777777",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_CLAIM_TEST",
        customer_id="CUS_CLAIM_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS10CD1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    repository = ClaimRepository(db)

    claim = Claim(
        claim_id="CLM_TEST_001",
        customer_id="CUS_CLAIM_TEST",
        policy_id="POL_CLAIM_TEST",
        incident_date=date(2026, 8, 20),
        claim_date=date(2026, 8, 21),
        claim_type="ACCIDENT",
        description="Vehicle damaged in a road accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    created_claim = repository.create(claim)

    assert created_claim.claim_id == "CLM_TEST_001"
    assert created_claim.customer_id == "CUS_CLAIM_TEST"
    assert created_claim.policy_id == "POL_CLAIM_TEST"

    retrieved_claim = repository.get_by_id("CLM_TEST_001")

    assert retrieved_claim is not None
    assert retrieved_claim.claim_id == "CLM_TEST_001"
    assert retrieved_claim.customer_id == "CUS_CLAIM_TEST"
    assert retrieved_claim.policy_id == "POL_CLAIM_TEST"
    assert retrieved_claim.claim_type == "ACCIDENT"
    assert retrieved_claim.claim_amount == 150000
    assert retrieved_claim.status == "SUBMITTED"

    assert retrieved_claim.fraud_score is None
    assert retrieved_claim.decision is None
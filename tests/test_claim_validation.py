from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.services.claim_service import ClaimService


def create_test_claim(db, claim_id: str, claim_status: str, policy_status: str):
    customer = Customer(
        customer_id=f"CUS_{claim_id}",
        name="Validation Test Customer",
        email=f"{claim_id.lower()}@example.com",
        phone="2222222222",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id=f"POL_{claim_id}",
        customer_id=f"CUS_{claim_id}",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS14KL1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status=policy_status,
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id=claim_id,
        customer_id=f"CUS_{claim_id}",
        policy_id=f"POL_{claim_id}",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status=claim_status,
    )

    repository = ClaimRepository(db)

    return repository.create(claim)


def test_submitted_claim_with_active_policy_is_valid(db):
    create_test_claim(
        db,
        "CLM_ACTIVE_POLICY",
        "SUBMITTED",
        "ACTIVE",
    )

    service = ClaimService(db)

    result = service.validate_claim("CLM_ACTIVE_POLICY")

    assert result is True


def test_submitted_claim_with_expired_policy_is_invalid(db):
    create_test_claim(
        db,
        "CLM_EXPIRED_POLICY",
        "SUBMITTED",
        "EXPIRED",
    )

    service = ClaimService(db)

    result = service.validate_claim("CLM_EXPIRED_POLICY")

    assert result is False


def test_rejected_claim_is_invalid(db):
    create_test_claim(
        db,
        "CLM_REJECTED",
        "REJECTED",
        "ACTIVE",
    )

    service = ClaimService(db)

    result = service.validate_claim("CLM_REJECTED")

    assert result is False
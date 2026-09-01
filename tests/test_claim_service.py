from datetime import date

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository
from app.services.claim_service import ClaimService


def test_get_claim(db):
    customer = Customer(
        customer_id="CUS_CLAIM_SERVICE_TEST",
        name="Claim Service Customer",
        email="claimservice@example.com",
        phone="3333333333",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_CLAIM_SERVICE_TEST",
        customer_id="CUS_CLAIM_SERVICE_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS13IJ1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_SERVICE_TEST",
        customer_id="CUS_CLAIM_SERVICE_TEST",
        policy_id="POL_CLAIM_SERVICE_TEST",
        incident_date=date(2026, 8, 25),
        claim_date=date(2026, 8, 26),
        claim_type="ACCIDENT",
        description="Vehicle damaged in an accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    service = ClaimService(db)

    result = service.get_claim("CLM_SERVICE_TEST")

    assert result is not None
    assert result.claim_id == "CLM_SERVICE_TEST"
    assert result.customer_id == "CUS_CLAIM_SERVICE_TEST"
    assert result.policy_id == "POL_CLAIM_SERVICE_TEST"
    assert result.claim_type == "ACCIDENT"
    assert result.claim_amount == 150000
    assert result.status == "SUBMITTED"
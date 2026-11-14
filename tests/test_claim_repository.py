
from datetime import date

import pytest

from app.database.models import Claim, Customer, Policy
from app.repositories.claim_repository import ClaimRepository


def create_customer_and_policy(db, suffix="TEST"):
    customer_id = f"CUS_REPO_{suffix}"
    policy_id = f"POL_REPO_{suffix}"

    customer = Customer(
        customer_id=customer_id,
        name="Repository Test Customer",
        email=f"repo_{suffix}@example.com",
        phone="7777777777",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id=policy_id,
        customer_id=customer_id,
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

    return customer_id, policy_id


def create_claim(
    repository,
    customer_id,
    policy_id,
    claim_id,
    incident_date,
    claim_date,
    claim_type="ACCIDENT",
):
    claim = Claim(
        claim_id=claim_id,
        customer_id=customer_id,
        policy_id=policy_id,
        incident_date=incident_date,
        claim_date=claim_date,
        claim_type=claim_type,
        description="Vehicle damaged in a road accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    return repository.create(claim)


def test_create_and_get_claim(db):
    customer_id, policy_id = create_customer_and_policy(
        db, "CREATE"
    )

    repository = ClaimRepository(db)

    claim = Claim(
        claim_id="CLM_TEST_001",
        customer_id=customer_id,
        policy_id=policy_id,
        incident_date=date(2026, 8, 20),
        claim_date=date(2026, 8, 21),
        claim_type="ACCIDENT",
        description="Vehicle damaged in a road accident",
        claim_amount=150000,
        status="SUBMITTED",
    )

    created_claim = repository.create(claim)

    assert created_claim.claim_id == "CLM_TEST_001"
    assert created_claim.customer_id == customer_id
    assert created_claim.policy_id == policy_id

    retrieved_claim = repository.get_by_id("CLM_TEST_001")

    assert retrieved_claim is not None
    assert retrieved_claim.claim_id == "CLM_TEST_001"
    assert retrieved_claim.customer_id == customer_id
    assert retrieved_claim.policy_id == policy_id
    assert retrieved_claim.claim_type == "ACCIDENT"
    assert retrieved_claim.claim_amount == 150000
    assert retrieved_claim.status == "SUBMITTED"

    assert retrieved_claim.fraud_score is None
    assert retrieved_claim.decision is None


def test_find_duplicate_claim_returns_true(db):
    customer_id, policy_id = create_customer_and_policy(
        db, "DUPLICATE"
    )

    repository = ClaimRepository(db)

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_DUP_001",
        date(2026, 8, 20),
        date(2026, 8, 21),
    )

    result = repository.find_duplicate_claim(
        policy_id=policy_id,
        incident_date=date(2026, 8, 20),
        claim_type="ACCIDENT",
    )

    assert result is True


def test_find_duplicate_claim_returns_false(db):
    customer_id, policy_id = create_customer_and_policy(
        db, "NO_DUPLICATE"
    )

    repository = ClaimRepository(db)

    result = repository.find_duplicate_claim(
        policy_id=policy_id,
        incident_date=date(2026, 8, 20),
        claim_type="ACCIDENT",
    )

    assert result is False


def test_find_duplicate_claim_excludes_current_claim(db):
    customer_id, policy_id = create_customer_and_policy(
        db, "EXCLUDE_DUPLICATE"
    )

    repository = ClaimRepository(db)

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_DUP_002",
        date(2026, 8, 20),
        date(2026, 8, 21),
    )

    result = repository.find_duplicate_claim(
        policy_id=policy_id,
        incident_date=date(2026, 8, 20),
        claim_type="ACCIDENT",
        exclude_claim_id="CLM_DUP_002",
    )

    assert result is False


def test_count_recent_claims(db):
    customer_id, policy_id = create_customer_and_policy(
        db, "RECENT"
    )

    repository = ClaimRepository(db)

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_RECENT_001",
        date(2026, 9, 20),
        date(2026, 9, 21),
    )

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_RECENT_002",
        date(2026, 8, 10),
        date(2026, 8, 11),
    )

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_OLD_001",
        date(2026, 6, 20),
        date(2026, 6, 21),
    )

    result = repository.count_recent_claims(
        customer_id=customer_id,
        reference_date=date(2026, 10, 1),
        window_days=90,
    )

    assert result == 2


def test_count_recent_claims_excludes_current_claim(db):
    customer_id, policy_id = create_customer_and_policy(
        db, "EXCLUDE_RECENT"
    )

    repository = ClaimRepository(db)

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_RECENT_003",
        date(2026, 9, 20),
        date(2026, 9, 21),
    )

    create_claim(
        repository,
        customer_id,
        policy_id,
        "CLM_RECENT_004",
        date(2026, 8, 10),
        date(2026, 8, 11),
    )

    result = repository.count_recent_claims(
        customer_id=customer_id,
        reference_date=date(2026, 10, 1),
        window_days=90,
        exclude_claim_id="CLM_RECENT_003",
    )

    assert result == 1


def test_count_recent_claims_rejects_invalid_window(db):
    repository = ClaimRepository(db)

    with pytest.raises(
        ValueError,
        match="Window days must be greater than zero",
    ):
        repository.count_recent_claims(
            customer_id="CUS_INVALID",
            reference_date=date(2026, 10, 1),
            window_days=0,
        )

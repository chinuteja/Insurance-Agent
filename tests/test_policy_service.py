from datetime import date

from app.database.models import Customer, Policy
from app.repositories.policy_repository import PolicyRepository
from app.services.policy_service import PolicyService


def test_get_policy(db):
    customer = Customer(
        customer_id="CUS_POLICY_SERVICE_TEST",
        name="Policy Service Customer",
        email="policyservice@example.com",
        phone="3333333333",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_SERVICE_TEST",
        customer_id="CUS_POLICY_SERVICE_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS17QR1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    repository = PolicyRepository(db)
    repository.create(policy)

    service = PolicyService(db)

    result = service.get_policy("POL_SERVICE_TEST")

    assert result is not None
    assert result.policy_id == "POL_SERVICE_TEST"
    assert result.customer_id == "CUS_POLICY_SERVICE_TEST"
    assert result.status == "ACTIVE"


def test_is_policy_active_returns_true_for_active_policy(db):
    customer = Customer(
        customer_id="CUS_ACTIVE_POLICY_TEST",
        name="Active Policy Customer",
        email="activepolicy@example.com",
        phone="3333333334",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_ACTIVE_TEST",
        customer_id="CUS_ACTIVE_POLICY_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS17QR5678",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    repository = PolicyRepository(db)
    repository.create(policy)

    service = PolicyService(db)

    result = service.is_policy_active("POL_ACTIVE_TEST")

    assert result is True


def test_is_policy_active_returns_false_for_expired_policy(db):
    customer = Customer(
        customer_id="CUS_EXPIRED_POLICY_TEST",
        name="Expired Policy Customer",
        email="expiredpolicy@example.com",
        phone="3333333335",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_EXPIRED_TEST",
        customer_id="CUS_EXPIRED_POLICY_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS17QR9999",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="EXPIRED",
    )

    repository = PolicyRepository(db)
    repository.create(policy)

    service = PolicyService(db)

    result = service.is_policy_active("POL_EXPIRED_TEST")

    assert result is False


def test_is_policy_active_returns_false_for_missing_policy(db):
    service = PolicyService(db)

    result = service.is_policy_active("POL_DOES_NOT_EXIST")

    assert result is False

def test_is_incident_covered_returns_true_when_incident_is_within_policy_period(db):
    customer = Customer(
        customer_id="CUS_COVERED_TEST",
        name="Covered Incident Customer",
        email="covered@example.com",
        phone="3333333336",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_COVERED_TEST",
        customer_id="CUS_COVERED_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS18AB1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    repository = PolicyRepository(db)
    repository.create(policy)

    service = PolicyService(db)

    result = service.is_incident_covered(
        "POL_COVERED_TEST",
        date(2026, 8, 25),
    )

    assert result is True


def test_is_incident_covered_returns_false_when_incident_is_outside_policy_period(db):
    customer = Customer(
        customer_id="CUS_NOT_COVERED_TEST",
        name="Not Covered Incident Customer",
        email="notcovered@example.com",
        phone="3333333337",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_NOT_COVERED_TEST",
        customer_id="CUS_NOT_COVERED_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS18AB5678",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=30000,
        coverage_amount=1000000,
        status="ACTIVE",
    )

    repository = PolicyRepository(db)
    repository.create(policy)

    service = PolicyService(db)

    result = service.is_incident_covered(
        "POL_NOT_COVERED_TEST",
        date(2027, 1, 10),
    )

    assert result is False
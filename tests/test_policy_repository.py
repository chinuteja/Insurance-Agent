from datetime import date

from app.database.models import Customer, Policy
from app.repositories.policy_repository import PolicyRepository


def test_create_and_get_policy(db):
    customer = Customer(
        customer_id="CUS_POLICY_TEST",
        name="Policy Test Customer",
        email="policytest@example.com",
        phone="8888888888",
    )

    db.add(customer)
    db.commit()

    repository = PolicyRepository(db)

    policy = Policy(
        policy_id="POL_TEST_001",
        customer_id="CUS_POLICY_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS09AB5678",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000,
        coverage_amount=800000,
        status="ACTIVE",
    )

    created_policy = repository.create(policy)

    assert created_policy.policy_id == "POL_TEST_001"
    assert created_policy.customer_id == "CUS_POLICY_TEST"

    retrieved_policy = repository.get_by_id("POL_TEST_001")

    assert retrieved_policy is not None
    assert retrieved_policy.policy_id == "POL_TEST_001"
    assert retrieved_policy.customer_id == "CUS_POLICY_TEST"
    assert retrieved_policy.policy_type == "COMPREHENSIVE"
    assert retrieved_policy.status == "ACTIVE"
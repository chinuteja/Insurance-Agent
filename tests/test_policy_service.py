from datetime import date

from app.database.models import Customer, Policy
from app.repositories.policy_repository import PolicyRepository
from app.services.policy_service import PolicyService


def test_get_policy(db):
    customer = Customer(
        customer_id="CUS_POLICY_SERVICE_TEST",
        name="Policy Service Customer",
        email="policyservice@example.com",
        phone="4444444444",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_SERVICE_TEST",
        customer_id="CUS_POLICY_SERVICE_TEST",
        policy_type="COMPREHENSIVE",
        vehicle_number="TS12GH7890",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=25000,
        coverage_amount=800000,
        status="ACTIVE",
    )

    repository = PolicyRepository(db)
    repository.create(policy)

    service = PolicyService(db)

    result = service.get_policy("POL_SERVICE_TEST")

    assert result is not None
    assert result.policy_id == "POL_SERVICE_TEST"
    assert result.customer_id == "CUS_POLICY_SERVICE_TEST"
    assert result.policy_type == "COMPREHENSIVE"
    assert result.status == "ACTIVE"
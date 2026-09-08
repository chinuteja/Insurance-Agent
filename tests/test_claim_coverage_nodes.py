from app.database.models import Customer, Policy, Claim
from app.graph.claim_coverage_nodes import create_coverage_node


def test_check_coverage_node(db):
    customer = Customer(
        customer_id="CUST_COVERAGE_NODE_001",
        name="Coverage Node Customer",
        email="coverage_node@test.com",
        phone="6666666666",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_COVERAGE_NODE_001",
        customer_id=customer.customer_id,
        policy_type="CAR",
        vehicle_number="TS12GH3456",
        start_date="2026-01-01",
        end_date="2026-12-31",
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_COVERAGE_NODE_001",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date="2026-06-01",
        claim_date="2026-06-02",
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
        fraud_score=None,
        decision=None,
    )

    db.add(claim)
    db.commit()

    state = {
        "claim_id": "CLM_COVERAGE_NODE_001",
        "claim_status": "SUBMITTED",
        "policy_status": "ACTIVE",
        "covered": None,
        "documents_present": None,
        "decision": None,
    }

    coverage_node = create_coverage_node(db)

    result = coverage_node(state)

    assert result == {
        "covered": True
    }
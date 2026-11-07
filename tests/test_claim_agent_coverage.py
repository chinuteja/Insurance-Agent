from unittest.mock import patch
from datetime import date

from app.database.models import Customer, Policy, Claim
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_claim_agent_coverage_flow(db):
    customer = Customer(
        customer_id="CUS_COVERAGE_E2E",
        name="Coverage E2E Customer",
        email="coveragee2e@test.com",
        phone="9999999994",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_COVERAGE_E2E",
        customer_id=customer.customer_id,
        policy_type="MOTOR",
        vehicle_number="TS09LM1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_COVERAGE_E2E",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date=date(2026, 9, 1),
        claim_date=date(2026, 9, 2),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
        fraud_score=0.0,
        decision=None,
    )
    db.add(claim)
    db.commit()

    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": claim.claim_id,
        "messages": [
            f"Is the accident covered by the policy for claim {claim.claim_id}?"
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = graph.invoke(state)

    assert result["intent"] == "COVERAGE"
    assert result["claim"]["claim_id"] == claim.claim_id
    assert result["policy_active"] is True
    assert result["covered"] is True

    response = result["messages"][-1]

    assert "does not guarantee final claim approval" in response



def test_coverage_with_missing_policy(db):
    from datetime import date

    from app.database.models import Customer, Policy, Claim
    from app.graph.claim_agent_coverage import (
        create_claim_coverage_node,
    )

    customer = Customer(
        customer_id="CUS_MISSING_POLICY",
        name="Missing Policy Customer",
        email="missing_policy@test.com",
        phone="9999999999",
    )

    db.add(customer)
    db.flush()

    policy = Policy(
        policy_id="POL_MISSING_POLICY",
        customer_id=customer.customer_id,
        policy_type="MOTOR",
        vehicle_number="TS09AB1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=10000,
        coverage_amount=500000,
        status="ACTIVE",
    )

    db.add(policy)
    db.flush()

    claim = Claim(
        claim_id="CLM_MISSING_POLICY",
        customer_id=customer.customer_id,
        policy_id=policy.policy_id,
        incident_date=date(2026, 9, 1),
        claim_date=date(2026, 9, 2),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=50000,
        status="SUBMITTED",
        fraud_score=0.0,
        decision=None,
    )

    db.add(claim)
    db.commit()

    node = create_claim_coverage_node(db)

    state = {
        "claim_id": claim.claim_id,
        "messages": ["Is my accident covered?"],
        "intent": "COVERAGE",
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    with patch(
    "app.graph.claim_agent_coverage.PolicyService.get_policy",
    return_value=None,):
        result = node(state)
    assert result["policy_active"] is False
    assert result["covered"] is False
    assert "was not found" in result["decision_reason"]
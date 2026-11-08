from datetime import date
from unittest.mock import patch

from app.database.models import Customer, Policy, Claim
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_claim_agent_handles_missing_policy(db):
    customer = Customer(
        customer_id="CUS_GRAPH_MISSING",
        name="Missing Policy Customer",
        email="missing_graph@test.com",
        phone="9999999999",
    )

    db.add(customer)
    db.flush()

    policy = Policy(
        policy_id="POL_GRAPH_MISSING",
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
        claim_id="CLM_GRAPH_MISSING",
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

    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": claim.claim_id,
        "messages": [
            "Is my accident covered by my policy?"
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    with patch(
        "app.graph.claim_agent_coverage.PolicyService.get_policy",
        return_value=None,
    ):
        result = graph.invoke(state)

    assert result["intent"] == "COVERAGE"
    assert result["policy_active"] is False
    assert result["covered"] is False
    assert len(result["messages"]) > 1

    response = result["messages"][-1]

    assert isinstance(response, str)
    assert "not found" in response.lower()
    assert "coverage cannot be confirmed" in response.lower()
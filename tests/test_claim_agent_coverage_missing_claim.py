from datetime import date
from unittest.mock import patch
from app.exceptions.business_exceptions import ClaimNotFoundException
from app.database.models import Customer, Policy
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_coverage_with_missing_claim(db):

    customer = Customer(
        customer_id="CUS_COV_MISSING_CLAIM",
        name="Coverage Test Customer",
        email="coverage_missing@test.com",
        phone="9999999999",
    )

    db.add(customer)
    db.flush()

    policy = Policy(
        policy_id="POL_COV_MISSING_CLAIM",
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
    db.commit()

    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": "CLM_INVALID_999",
        "messages": [
            "Is claim CLM_INVALID_999 covered by my policy?"
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
        "app.graph.claim_agent_coverage.ClaimService.get_claim",
        side_effect=ClaimNotFoundException("Claim not found"),
        # side_effect=Exception("Claim not found"),
    ):
        result = graph.invoke(state)

    assert result["intent"] == "COVERAGE"
    assert result["claim"] is None
    assert len(result["messages"]) > 1

    response = result["messages"][-1]

    assert isinstance(response, str)
    assert "CLM_INVALID_999" in response
    assert "couldn't find" in response.lower()

from datetime import date

from app.database.models import Customer, Policy, Claim
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_analysis_with_inactive_policy(db):

    customer = Customer(
        customer_id="CUS_INACTIVE_TEST",
        name="Inactive Policy Customer",
        email="inactive@test.com",
        phone="9999999999",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_INACTIVE_TEST",
        customer_id="CUS_INACTIVE_TEST",
        policy_type="AUTO",
        vehicle_number="TS09INACTIVE",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=20000,
        coverage_amount=500000,
        status="INACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_INACTIVE_TEST",
        customer_id="CUS_INACTIVE_TEST",
        policy_id="POL_INACTIVE_TEST",
        incident_date=date(2026, 6, 15),
        claim_date=date(2026, 6, 16),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
    )
    db.add(claim)
    db.commit()

    state = {
        "claim_id": "CLM_INACTIVE_TEST",
        "messages": [
            "Analyze claim CLM_INACTIVE_TEST and tell me whether it is eligible."
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    graph = create_claim_agent_graph(db)
    result = graph.invoke(state)

    assert result["intent"] == "ANALYSIS"
    assert result["decision"] == "NEEDS_REVIEW"
    assert "not active" in result["messages"][-1].lower()

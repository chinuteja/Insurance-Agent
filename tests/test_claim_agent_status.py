from datetime import date

from app.database.models import Customer, Policy, Claim
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_claim_agent_status_flow(db):
    customer = Customer(
        customer_id="CUS_STATUS_001",
        name="Status Test Customer",
        email="status@test.com",
        phone="9999999999",
    )

    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_STATUS_001",
        customer_id=customer.customer_id,
        policy_type="MOTOR",
        vehicle_number="TS09AB1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )

    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_STATUS_001",
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
            f"What is the status of claim {claim.claim_id}?"
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

    assert result["intent"] == "STATUS"
    assert result["claim"] is not None
    assert result["claim"]["claim_id"] == claim.claim_id
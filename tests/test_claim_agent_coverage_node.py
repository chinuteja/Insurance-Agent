
from datetime import date

from app.database.models import Customer, Policy, Claim
from app.graph.claim_agent_coverage import create_claim_coverage_node


def test_claim_coverage_node_checks_incident_date(db):
    customer = Customer(
        customer_id="CUS_COVER_NODE",
        name="Coverage Node Customer",
        email="covernode@test.com",
        phone="9999999996",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_COVER_NODE",
        customer_id=customer.customer_id,
        policy_type="MOTOR",
        vehicle_number="TS09GH1234",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=15000,
        coverage_amount=500000,
        status="ACTIVE",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_COVER_NODE",
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

    node = create_claim_coverage_node(db)

    result = node({
        "claim_id": claim.claim_id,
        "messages": [],
        "intent": "COVERAGE",
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    })

    assert result["claim"]["claim_id"] == claim.claim_id
    assert result["policy_active"] is True
    assert result["covered"] is True
    assert "does not guarantee" in result["decision_reason"]

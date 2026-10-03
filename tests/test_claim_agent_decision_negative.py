from datetime import date

from app.database.models import Customer, Policy, Claim
from app.repositories.claim_repository import ClaimRepository
from app.graph.claim_agent_decision import create_claim_decision_node


def test_claim_decision_inactive_policy(db):
    customer = Customer(
        customer_id="CUST_DECISION_NEG",
        name="Negative Test Customer",
        email="decision_neg@test.com",
        phone="8888888888",
    )
    db.add(customer)
    db.commit()

    policy = Policy(
        policy_id="POL_DECISION_NEG",
        customer_id="CUST_DECISION_NEG",
        policy_type="AUTO",
        vehicle_number="TS09NEG123",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
        premium=20000,
        coverage_amount=500000,
        status="EXPIRED",
    )
    db.add(policy)
    db.commit()

    claim = Claim(
        claim_id="CLM_DECISION_NEG",
        customer_id="CUST_DECISION_NEG",
        policy_id="POL_DECISION_NEG",
        incident_date=date(2026, 6, 15),
        claim_date=date(2026, 6, 16),
        claim_type="ACCIDENT",
        description="Vehicle accident",
        claim_amount=100000,
        status="SUBMITTED",
    )

    repository = ClaimRepository(db)
    repository.create(claim)

    decision_node = create_claim_decision_node(db)

    result = decision_node(
        {
            "claim_id": "CLM_DECISION_NEG",
            "messages": [],
            "claim": None,
            "policy_active": None,
            "covered": None,
            "documents_present": None,
            "decision": None,
            "decision_reason": None,
        }
    )

    assert result["decision"] == "NEEDS_REVIEW"
    assert "not active" in result["decision_reason"]
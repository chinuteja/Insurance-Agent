from app.graph.claim_agent_context import build_claim_context


def test_build_claim_context():
    state = {
        "claim_id": "CLM_CONTEXT",
        "messages": [],
        "claim": {
            "claim_id": "CLM_CONTEXT",
            "customer_id": "CUST_CONTEXT",
            "policy_id": "POL_CONTEXT",
            "claim_type": "ACCIDENT",
            "claim_amount": 150000,
            "incident_date": "2026-06-15",
            "claim_date": "2026-06-16",
            "status": "SUBMITTED",
            "description": "Vehicle accident",
        },
        "policy_active": True,
        "covered": True,
        "documents_present": True,
        "decision": "ELIGIBLE_FOR_REVIEW",
        "decision_reason": None,
    }

    context = build_claim_context(state)

    assert "CLM_CONTEXT" in context
    assert "CUST_CONTEXT" in context
    assert "POL_CONTEXT" in context
    assert "ACCIDENT" in context
    assert "150000" in context
    assert "Policy Active: True" in context
    assert "Incident Covered: True" in context
    assert "Documents Present: True" in context
    assert "ELIGIBLE_FOR_REVIEW" in context
from app.graph.claim_agent_analysis import build_claim_analysis


def test_build_claim_analysis():
    state = {
        "claim_id": "CLM_ANALYSIS",
        "messages": [],
        "claim": {
            "claim_id": "CLM_ANALYSIS",
            "customer_id": "CUST_ANALYSIS",
            "policy_id": "POL_ANALYSIS",
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

    analysis = build_claim_analysis(state)

    assert "CLM_ANALYSIS" in analysis
    assert "150000" in analysis
    assert "ACCIDENT" in analysis
    assert "policy is active" in analysis
    assert "incident is covered" in analysis
    assert "required documents are present" in analysis
    assert "ELIGIBLE_FOR_REVIEW" in analysis
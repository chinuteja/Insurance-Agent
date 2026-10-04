from app.graph.claim_agent_llm_response import create_claim_llm_response_node


def test_claim_llm_response_node(db):
    node = create_claim_llm_response_node(db)

    state = {
        "claim_id": "CLM_LLM_RESPONSE",
        "messages": [],
        "claim": {
            "claim_id": "CLM_LLM_RESPONSE",
            "customer_id": "CUST_LLM_RESPONSE",
            "policy_id": "POL_LLM_RESPONSE",
            "claim_type": "ACCIDENT",
            "claim_amount": 100000,
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

    result = node(state)

    assert "messages" in result
    assert len(result["messages"]) == 1

    response = result["messages"][-1]

    assert isinstance(response, str)
    assert len(response) > 0
from app.graph.claim_agent_intent_router import route_after_intent


def test_status_intent_routes_to_status():
    state = {
        "claim_id": "CLM_STATUS",
        "messages": [
            "What is the status of claim CLM_STATUS?"
        ],
        "intent": "STATUS",
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = route_after_intent(state)

    assert result == "status"


def test_analysis_intent_routes_to_agent():
    state = {
        "claim_id": "CLM_ANALYSIS",
        "messages": [
            "Can claim CLM_ANALYSIS be approved?"
        ],
        "intent": "ANALYSIS",
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = route_after_intent(state)

    assert result == "agent"
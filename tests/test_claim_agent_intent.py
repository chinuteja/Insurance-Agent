from app.graph.claim_agent_intent import create_claim_intent_node


def test_claim_intent_analysis(db):
    node = create_claim_intent_node(db)

    state = {
        "claim_id": "CLM_INTENT",
        "messages": [
            "Can claim CLM_INTENT be approved?"
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = node(state)

    assert result["intent"] == "ANALYSIS"
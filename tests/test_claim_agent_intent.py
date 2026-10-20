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


def test_claim_intent_coverage(db):
    node = create_claim_intent_node(db)

    state = {
        "claim_id": "CLM_COVERAGE",
        "messages": [
            "Is the accident covered by my insurance policy?"
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

    assert result["intent"] == "COVERAGE"

def test_claim_intent_analysis_request(db):
    node = create_claim_intent_node(db)

    state = {
        "claim_id": "CLM_ANALYSIS",
        "messages": [
            "Analyze claim CLM_ANALYSIS and explain whether it is eligible for approval."
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

from app.graph.claim_agent_general import create_claim_general_node


def test_claim_general_node_answers_general_question():
    node = create_claim_general_node()

    state = {
        "claim_id": "",
        "messages": [
            "What documents are generally required to file a motor insurance claim?"
        ],
        "intent": "GENERAL",
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = node(state)

    assert len(result["messages"]) > 1
    assert isinstance(result["messages"][-1], str)
    assert len(result["messages"][-1]) > 0

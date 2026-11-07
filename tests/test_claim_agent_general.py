
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_claim_agent_general_question(db):
    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": "CLM_GENERAL",
        "messages": [
            "What documents are generally required to file a motor insurance claim?"
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

    assert result["intent"] == "GENERAL"
    assert len(result["messages"]) > 1
    assert isinstance(result["messages"][-1], str)

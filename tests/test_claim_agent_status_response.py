from app.graph.claim_agent_status_response import (
    create_claim_status_response_node,
)


def test_claim_status_response_node():

    node = create_claim_status_response_node()

    state = {
        "claim_id": "CLM_STATUS_001",
        "messages": ["What is my claim status?"],
        "intent": "STATUS",
        "claim": {
            "claim_id": "CLM_STATUS_001",
            "customer_id": "CUS_001",
            "policy_id": "POL_001",
            "claim_type": "ACCIDENT",
            "claim_amount": 50000,
            "status": "SUBMITTED",
            "incident_date": "2026-05-10",
            "claim_date": "2026-05-11",
        },
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    result = node(state)

    assert len(result["messages"]) == 2

    response = result["messages"][-1]

    assert "CLM_STATUS_001" in response
    assert "SUBMITTED" in response
    assert "2026-05-11" in response
    assert "50000" in response
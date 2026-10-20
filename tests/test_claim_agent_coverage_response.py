
from app.graph.claim_agent_coverage_response import (
    create_claim_coverage_response_node,
)


def test_coverage_response_does_not_promise_approval():
    node = create_claim_coverage_response_node()

    state = {
        "claim_id": "CLM_RESPONSE",
        "messages": [
            "Is my accident covered?"
        ],
        "intent": "COVERAGE",
        "claim": {
            "claim_id": "CLM_RESPONSE",
            "incident_date": "2026-09-01",
        },
        "policy_active": True,
        "covered": True,
        "documents_present": None,
        "decision": None,
        "decision_reason": "The incident date falls within the policy coverage period.",
    }

    result = node(state)

    response = result["messages"][-1]

    assert "CLM_RESPONSE" in response
    assert "does not guarantee final claim approval" in response

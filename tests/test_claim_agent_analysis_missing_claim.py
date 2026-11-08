from unittest.mock import patch

from app.exceptions.business_exceptions import ClaimNotFoundException
from app.graph.claim_agent_graph import create_claim_agent_graph


def test_analysis_with_missing_claim(db):

    graph = create_claim_agent_graph(db)

    state = {
        "claim_id": "CLM_ANALYSIS_INVALID",
        "messages": [
            "Analyze claim CLM_ANALYSIS_INVALID and tell me whether it is eligible."
        ],
        "intent": None,
        "claim": None,
        "policy_active": None,
        "covered": None,
        "documents_present": None,
        "decision": None,
        "decision_reason": None,
    }

    with patch(
        "app.graph.claim_agent_data.ClaimService.get_claim",
        side_effect=ClaimNotFoundException(
            "Claim not found"
        ),
    ):
        result = graph.invoke(state)

    assert result["intent"] == "ANALYSIS"
    assert result["claim"] is None
    assert "CLM_ANALYSIS_INVALID" in result["messages"][-1]
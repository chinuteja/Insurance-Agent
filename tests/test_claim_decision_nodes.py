from app.graph.claim_decision_nodes import create_decision_node


def test_claim_decision_approved():
    decision_node = create_decision_node()

    state = {
        "claim_id": "CLM_DECISION_001",
        "claim_status": "SUBMITTED",
        "policy_status": "ACTIVE",
        "covered": True,
        "documents_present": True,
        "decision": None,
    }

    result = decision_node(state)

    assert result == {
        "decision": "APPROVED"
    }


def test_claim_decision_rejected():
    decision_node = create_decision_node()

    state = {
        "claim_id": "CLM_DECISION_002",
        "claim_status": "SUBMITTED",
        "policy_status": "ACTIVE",
        "covered": False,
        "documents_present": True,
        "decision": None,
    }

    result = decision_node(state)

    assert result == {
        "decision": "REJECTED"
    }
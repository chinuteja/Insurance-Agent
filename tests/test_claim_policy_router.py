from app.graph.claim_policy_nodes import route_after_policy


def test_route_after_policy_active():
    state = {
        "claim_id": "CLM_ROUTER_001",
        "claim_status": "SUBMITTED",
        "policy_status": "ACTIVE",
        "covered": None,
        "documents_present": None,
        "decision": None,
    }

    result = route_after_policy(state)

    assert result == "check_coverage"


def test_route_after_policy_inactive():
    state = {
        "claim_id": "CLM_ROUTER_002",
        "claim_status": "SUBMITTED",
        "policy_status": "INACTIVE",
        "covered": None,
        "documents_present": None,
        "decision": None,
    }

    result = route_after_policy(state)

    assert result == "make_decision"
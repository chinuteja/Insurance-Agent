from app.graph.claim_agent_intent_router import route_after_intent


def test_status_intent_routes_to_status():
    state = {"intent": "STATUS"}

    assert route_after_intent(state) == "status"


def test_coverage_intent_routes_to_coverage():
    state = {"intent": "COVERAGE"}

    assert route_after_intent(state) == "coverage"


def test_analysis_intent_routes_to_agent():
    state = {"intent": "ANALYSIS"}

    assert route_after_intent(state) == "agent"


def test_general_intent_routes_to_agent():
    state = {"intent": "GENERAL"}

    assert route_after_intent(state) == "agent"
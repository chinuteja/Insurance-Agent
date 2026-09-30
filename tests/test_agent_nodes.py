from app.graph.agent_nodes import mock_agent_node, route_after_agent


def test_mock_agent_node():
    state = {
        "message": "Process claim CLM001",
        "tool_called": None,
        "tool_result": None,
        "response": None,
    }

    result = mock_agent_node(state)

    assert result == {
        "tool_called": "get_claim"
    }


def test_route_after_agent_to_tool():
    state = {
        "message": "Process claim CLM001",
        "tool_called": "get_claim",
        "tool_result": None,
        "response": None,
    }

    result = route_after_agent(state)

    assert result == "tool"


def test_route_after_agent_to_end():
    state = {
        "message": "Process claim CLM001",
        "tool_called": "get_claim",
        "tool_result": "Claim CLM001 is SUBMITTED",
        "response": None,
    }

    result = route_after_agent(state)

    assert result == "end"
from app.graph.agent_nodes import mock_agent_node


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
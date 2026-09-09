from app.graph.agent_tool_nodes import mock_tool_node


def test_mock_tool_node():
    state = {
        "message": "Process claim CLM001",
        "tool_called": "get_claim",
        "tool_result": None,
        "response": None,
    }

    result = mock_tool_node(state)

    assert result == {
        "tool_result": "Claim CLM001 is SUBMITTED"
    }
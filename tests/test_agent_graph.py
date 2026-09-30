from app.graph.agent_graph import create_agent_graph


def test_agent_tool_loop():

    graph = create_agent_graph()

    state = {
        "message": "Process claim CLM001",
        "tool_called": None,
        "tool_result": None,
        "response": None,
    }

    result = graph.invoke(state)

    assert result["tool_called"] == "get_claim"
    assert result["tool_result"] == "Claim CLM001 is SUBMITTED"
    assert result["response"] == "I have the claim information."
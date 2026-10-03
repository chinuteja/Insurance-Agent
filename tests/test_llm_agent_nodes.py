from app.graph.llm_agent_nodes import create_llm_agent_node


def test_llm_agent_node(db):

    agent_node = create_llm_agent_node(db)

    state = {
        "messages": [
            "Get claim CLM_NODE_TEST"
        ]
    }

    result = agent_node(state)

    assert "messages" in result

    assert len(result["messages"]) == 2

    response = result["messages"][-1]

    assert len(response.tool_calls) > 0

    assert response.tool_calls[0]["name"] == "get_claim"
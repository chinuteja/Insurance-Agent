from app.graph.agent_state import AgentState


def mock_agent_node(state: AgentState) -> dict:
    return {
        "tool_called": "get_claim"
    }
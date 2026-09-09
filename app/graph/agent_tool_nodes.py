from app.graph.agent_state import AgentState


def mock_tool_node(state: AgentState) -> dict:
    if state["tool_called"] == "get_claim":
        return {
            "tool_result": "Claim CLM001 is SUBMITTED"
        }

    return {
        "tool_result": "Unknown tool"
    }
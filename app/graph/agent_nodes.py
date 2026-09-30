from app.graph.agent_state import AgentState


def mock_agent_node(state: AgentState) -> dict:
    if state["tool_result"] is None:
        return {
            "tool_called": "get_claim"
        }

    return {
        "response": "I have the claim information."
    }


def route_after_agent(state: AgentState) -> str:
    if state["tool_called"] is not None and state["tool_result"] is None:
        return "tool"

    return "end"
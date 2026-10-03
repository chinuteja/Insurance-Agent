from app.graph.llm_agent_state import LLMAgentState


def route_after_llm(state: LLMAgentState) -> str:

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool"

    return "end"

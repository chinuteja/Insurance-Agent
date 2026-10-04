from app.graph.claim_agent_state import ClaimAgentState


def route_after_intent(state: ClaimAgentState) -> str:
    intent = state["intent"]

    if intent == "STATUS":
        return "status"

    return "agent"
from app.graph.claim_agent_state import ClaimAgentState


def claim_agent_response_node(state: ClaimAgentState) -> dict:
    decision = state["decision"]

    if decision == "ELIGIBLE_FOR_REVIEW":
        response = (
            f"Claim {state['claim_id']} passed the current eligibility checks "
            "and is eligible for further review. "
            "This is not final claim approval."
        )

    elif decision == "NEEDS_REVIEW":
        reason = state.get("decision_reason")

        response = (
            f"Claim {state['claim_id']} cannot be automatically cleared "
            "under the current eligibility checks and requires further review."
        )

        if reason:
            response += f" Reason: {reason}"

    else:
        response = (
            f"Claim {state['claim_id']} could not be assigned "
            "a final eligibility status."
        )

    return {
        "messages": state["messages"] + [response]
    }
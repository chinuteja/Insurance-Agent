from app.graph.claim_agent_state import ClaimAgentState
from app.graph.claim_agent_analysis import build_claim_analysis


def claim_agent_response_node(state: ClaimAgentState) -> dict:
    analysis = build_claim_analysis(state)

    decision = state["decision"]

    if decision == "ELIGIBLE_FOR_REVIEW":
        response = (
            f"Claim {state['claim_id']} is eligible for further review.\n\n"
            f"{analysis}\n\n"
            "This is not final claim approval."
        )

    elif decision == "NEEDS_REVIEW":
        response = (
            f"Claim {state['claim_id']} requires further review.\n\n"
            f"{analysis}"
        )

    else:
        response = (
            f"Claim {state['claim_id']} could not be assigned "
            "a final eligibility status.\n\n"
            f"{analysis}"
        )

    return {
        "messages": state["messages"] + [response]
    }
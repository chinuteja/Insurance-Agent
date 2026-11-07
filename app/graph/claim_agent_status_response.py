from app.graph.claim_agent_state import ClaimAgentState


def create_claim_status_response_node():

    def claim_status_response_node(
        state: ClaimAgentState,
    ) -> dict:

        claim = state["claim"]

        message = (
            f"Your claim {claim['claim_id']} is currently "
            f"{claim['status']}. "
            f"It was filed on {claim['claim_date']} "
            f"for an amount of {claim['claim_amount']}. "
            f"The claim relates to a {claim['claim_type']} incident "
            f"reported on {claim['incident_date']}."
        )

        return {
            "messages": state["messages"] + [message]
        }

    return claim_status_response_node
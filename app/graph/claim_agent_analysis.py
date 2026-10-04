from app.graph.claim_agent_state import ClaimAgentState


def build_claim_analysis(state: ClaimAgentState) -> str:
    claim = state["claim"]

    analysis = (
        f"Claim {claim['claim_id']} was submitted with a claim amount of "
        f"{claim['claim_amount']} for a {claim['claim_type']} incident. "
        f"The policy is "
        f"{'active' if state['policy_active'] else 'not active'}, "
        f"the incident is "
        f"{'covered' if state['covered'] else 'not covered'}, "
        f"and required documents are "
        f"{'present' if state['documents_present'] else 'missing'}. "
        f"The deterministic eligibility result is "
        f"{state['decision']}."
    )

    if state.get("decision_reason"):
        analysis += f" Reason: {state['decision_reason']}"

    return analysis
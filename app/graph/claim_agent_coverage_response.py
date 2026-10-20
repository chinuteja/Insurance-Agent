
from app.graph.claim_agent_state import ClaimAgentState


def create_claim_coverage_response_node():
    def claim_coverage_response_node(
        state: ClaimAgentState,
    ) -> dict:
        claim = state["claim"]
        policy_active = state["policy_active"]
        covered = state["covered"]
        reason = state.get("decision_reason") or ""

        if not policy_active:
            message = (
                f"Claim {claim['claim_id']}: the policy is not active. "
                f"Coverage cannot be confirmed. {reason}"
            )
        elif covered:
            message = (
                f"Claim {claim['claim_id']}: the incident date "
                f"{claim['incident_date']} falls within the policy "
                f"coverage period. This is a date-based coverage check "
                f"only and does not guarantee final claim approval. "
                f"{reason}"
            )
        else:
            message = (
                f"Claim {claim['claim_id']}: the incident date "
                f"{claim['incident_date']} falls outside the policy "
                f"coverage period. {reason}"
            )

        return {
            "messages": state["messages"] + [message]
        }

    return claim_coverage_response_node

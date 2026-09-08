from app.graph.claim_state import ClaimState


def create_decision_node():

    def make_claim_decision(state: ClaimState) -> dict:
        if (
            state["claim_status"] == "SUBMITTED"
            and state["policy_status"] == "ACTIVE"
            and state["covered"] is True
            and state["documents_present"] is True
        ):
            return {
                "decision": "APPROVED"
            }

        return {
            "decision": "REJECTED"
        }

    return make_claim_decision

from app.graph.claim_agent_state import ClaimAgentState


def create_claim_supervisor_node():

    def supervisor_node(state: ClaimAgentState) -> dict:
        """
        Dynamically plans claim analysis using shared state.

        Preserves previous agent results and avoids scheduling
        agents that have already executed.
        """

        # Read existing shared state
        claim = state.get("claim")

        completed_agents = list(
            state.get("completed_agents") or []
        )

        agent_results = dict(
            state.get("agent_results") or {}
        )

        agent_errors = list(
            state.get("agent_errors") or []
        )

        # Build execution plan
        supervisor_plan = []

        if claim is not None:

            # Schedule document verification if not executed
            if "document_verification" not in completed_agents:
                supervisor_plan.append(
                    "document_verification"
                )

            # Schedule fraud detection if not executed
            if "fraud_detection" not in completed_agents:
                supervisor_plan.append(
                    "fraud_detection"
                )

        # Decision is the final processing step
        supervisor_plan.append("decision")

        # Identify the next component
        current_agent = (
            supervisor_plan[0]
            if supervisor_plan
            else None
        )

        return {
            "supervisor_plan": supervisor_plan,
            "completed_agents": completed_agents,
            "agent_results": agent_results,
            "current_agent": current_agent,
            "requires_human_review": state.get(
                "requires_human_review"
            ),
            "agent_errors": agent_errors,
        }

    return supervisor_node

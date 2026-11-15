
from app.graph.claim_agent_state import ClaimAgentState


def create_claim_supervisor_node():

    def supervisor_node(state: ClaimAgentState) -> dict:
        """
        Plans the execution of the existing claim analysis workflow.

        The supervisor identifies the components that need to execute.
        Actual execution and routing will be implemented in later steps.
        """

        supervisor_plan = [
            "data",
            "document_verification",
            "fraud_detection",
            "decision",
        ]

        return {
            "supervisor_plan": supervisor_plan,
            "completed_agents": [],
            "agent_results": {},
            "current_agent": "data",
            "requires_human_review": None,
            "agent_errors": [],
        }

    return supervisor_node

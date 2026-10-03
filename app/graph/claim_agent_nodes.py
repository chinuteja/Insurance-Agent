from sqlalchemy.orm import Session

from app.graph.claim_agent_state import ClaimAgentState
from app.graph.llm_agent import create_llm_agent


def create_claim_agent_node(db: Session):
    agent = create_llm_agent(db)

    def claim_agent_node(state: ClaimAgentState) -> dict:
        response = agent.invoke(state["messages"])

        return {
            "messages": state["messages"] + [response]
        }

    return claim_agent_node
from sqlalchemy.orm import Session

from app.graph.llm_agent_state import LLMAgentState
from app.graph.llm_agent import create_llm_agent


def create_llm_agent_node(db: Session):

    agent = create_llm_agent(db)

    def llm_agent_node(state: LLMAgentState) -> dict:

        response = agent.invoke(state["messages"])

        return {
            "messages": state["messages"] + [response]
        }

    return llm_agent_node
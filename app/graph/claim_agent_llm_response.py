from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.claim_agent_state import ClaimAgentState
from app.graph.claim_agent_analysis import build_claim_analysis
from app.llm import create_llm


def create_claim_llm_response_node(db: Session):
    llm = create_llm()

    def claim_llm_response_node(state: ClaimAgentState) -> dict:
        analysis = build_claim_analysis(state)

        system_prompt = """
You are an insurance claim assistant.

Your job is to explain the verified claim analysis to the user.

IMPORTANT RULES:
1. Do not change the eligibility decision.
2. Do not invent insurance facts.
3. Do not approve or reject a claim yourself.
4. Treat the deterministic eligibility result as authoritative.
5. Clearly explain why the claim received its current eligibility result.
6. If the result is ELIGIBLE_FOR_REVIEW, explicitly state that this
   does not mean final claim approval.
7. Keep the response concise and professional.
"""

        user_prompt = f"""
Explain the following verified insurance claim analysis to the customer:

{analysis}
"""

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )

        return {
            "messages": state["messages"] + [response.content]
        }

    return claim_llm_response_node
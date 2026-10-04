from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.claim_agent_state import ClaimAgentState
from app.llm import create_llm


def create_claim_intent_node(db: Session):
    llm = create_llm()

    def claim_intent_node(state: ClaimAgentState) -> dict:
        user_message = state["messages"][0]

        system_prompt = """
You are an insurance claim intent classifier.

Classify the user's request into exactly one of these intents:

STATUS
COVERAGE
ANALYSIS
GENERAL

Rules:

STATUS:
The user wants the current status of a claim.

COVERAGE:
The user wants to know whether an incident is covered by the policy.

ANALYSIS:
The user wants a broader analysis, eligibility explanation,
or wants to know whether a claim can proceed toward approval.

GENERAL:
The request does not clearly fit the above categories.

Return ONLY the intent name.
"""

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message),
            ]
        )

        intent = response.content.strip().upper()

        allowed_intents = {
            "STATUS",
            "COVERAGE",
            "ANALYSIS",
            "GENERAL",
        }

        if intent not in allowed_intents:
            intent = "GENERAL"

        return {
            "intent": intent
        }

    return claim_intent_node
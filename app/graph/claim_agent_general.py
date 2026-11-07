
from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.claim_agent_state import ClaimAgentState
from app.llm import create_llm


def create_claim_general_node():
    llm = create_llm()

    def claim_general_node(state: ClaimAgentState) -> dict:
        user_message = state["messages"][0]

        system_prompt = """
You are a helpful motor insurance assistant.

Your responsibilities:
1. Answer general motor insurance questions.
2. Explain common claim procedures and documentation.
3. Keep answers clear and easy to understand.
4. Never invent customer-specific policy or claim information.
5. Do not approve or reject insurance claims.
6. If a question requires specific policy information,
   explain that the policy document must be checked.

Keep your answers professional and concise.
"""

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message),
        ])

        return {
            "messages": state["messages"] + [response.content]
        }

    return claim_general_node

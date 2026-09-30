from sqlalchemy.orm import Session

from app.graph.agent_state import AgentState
from app.tools.claim_tools import create_claim_tools


def mock_tool_node(state: AgentState) -> dict:
    if state["tool_called"] == "get_claim":
        return {
            "tool_result": "Claim CLM001 is SUBMITTED"
        }

    return {
        "tool_result": "Unknown tool"
    }


def create_agent_tool_node(db: Session):

    claim_tools = create_claim_tools(db)

    get_claim_tool = next(
        tool
        for tool in claim_tools
        if tool.name == "get_claim"
    )

    def agent_tool_node(state: AgentState) -> dict:

        if state["tool_called"] == "get_claim":

            claim_id = state["message"].split()[-1]

            result = get_claim_tool.invoke(
                {"claim_id": claim_id}
            )

            return {
                "tool_result": str(result)
            }

        return {
            "tool_result": "Unknown tool"
        }

    return agent_tool_node
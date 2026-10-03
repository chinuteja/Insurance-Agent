
from sqlalchemy.orm import Session
from langchain_core.messages import ToolMessage

from app.graph.llm_agent_state import LLMAgentState
from app.tools.claim_tools import create_claim_tools


def create_llm_tool_node(db: Session):

    tools = create_claim_tools(db)

    tool_map = {
        tool.name: tool
        for tool in tools
    }

    def llm_tool_node(state: LLMAgentState) -> dict:

        last_message = state["messages"][-1]

        tool_messages = []

        for tool_call in last_message.tool_calls:

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_call_id = tool_call["id"]

            tool = tool_map[tool_name]

            result = tool.invoke(tool_args)

            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call_id,
                )
            )

        return {
            "messages": state["messages"] + tool_messages
        }

    return llm_tool_node

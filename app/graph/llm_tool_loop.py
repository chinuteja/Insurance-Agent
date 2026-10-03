from sqlalchemy.orm import Session

from app.graph.llm_agent import create_llm_agent
from app.tools.claim_tools import create_claim_tools


def run_llm_tool_loop(
    db: Session,
    message: str,
):
    agent = create_llm_agent(db)

    response = agent.invoke(message)

    if not response.tool_calls:
        return response.content

    tools = create_claim_tools(db)

    tool_map = {
        tool.name: tool
        for tool in tools
    }

    tool_results = []

    for tool_call in response.tool_calls:

        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        tool = tool_map[tool_name]

        result = tool.invoke(tool_args)

        tool_results.append(
            {
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "result": result,
            }
        )

    return {
        "assistant_response": response,
        "tool_results": tool_results,
    }
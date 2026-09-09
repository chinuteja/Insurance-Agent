from typing import TypedDict


class AgentState(TypedDict):
    message: str
    tool_called: str | None
    tool_result: str | None
    response: str | None
from langgraph.graph import StateGraph, START, END

from app.graph.agent_state import AgentState
from app.graph.agent_nodes import (
    mock_agent_node,
    route_after_agent,
)
from app.graph.agent_tool_nodes import mock_tool_node


def create_agent_graph():

    builder = StateGraph(AgentState)

    builder.add_node("agent", mock_agent_node)
    builder.add_node("tool", mock_tool_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tool": "tool",
            "end": END,
        },
    )

    builder.add_edge("tool", "agent")

    return builder.compile()
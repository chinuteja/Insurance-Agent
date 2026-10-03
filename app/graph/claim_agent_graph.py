from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.graph.claim_agent_state import ClaimAgentState
from app.graph.claim_agent_nodes import create_claim_agent_node
from app.graph.llm_tool_nodes import create_llm_tool_node
from app.graph.llm_agent_router import route_after_llm


def create_claim_agent_graph(db: Session):
    agent_node = create_claim_agent_node(db)
    tool_node = create_llm_tool_node(db)

    builder = StateGraph(ClaimAgentState)

    builder.add_node("agent", agent_node)
    builder.add_node("tool", tool_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent",
        route_after_llm,
        {
            "tool": "tool",
            "end": END,
        },
    )

    builder.add_edge("tool", "agent")

    return builder.compile()
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.graph.claim_agent_state import ClaimAgentState
from app.graph.claim_agent_nodes import create_claim_agent_node
from app.graph.claim_agent_intent import create_claim_intent_node
from app.graph.claim_agent_intent_router import route_after_intent
from app.graph.claim_agent_data import create_claim_data_node
from app.graph.llm_tool_nodes import create_llm_tool_node
from app.graph.llm_agent_router import route_after_llm
from app.graph.claim_agent_decision import create_claim_decision_node
from app.graph.claim_agent_llm_response import create_claim_llm_response_node


def create_claim_agent_graph(db: Session):
    intent_node = create_claim_intent_node(db)
    agent_node = create_claim_agent_node(db)
    data_node = create_claim_data_node(db)
    tool_node = create_llm_tool_node(db)
    decision_node = create_claim_decision_node(db)
    llm_response_node = create_claim_llm_response_node(db)

    builder = StateGraph(ClaimAgentState)

    builder.add_node("intent", intent_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tool", tool_node)
    builder.add_node("data", data_node)
    builder.add_node("decision", decision_node)
    builder.add_node("llm_response", llm_response_node)

    builder.add_edge(START, "intent")

    builder.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "status": "agent",
            "agent": "agent",
        },
    )

    builder.add_conditional_edges(
        "agent",
        route_after_llm,
        {
            "tool": "tool",
            "end": "data",
        },
    )

    builder.add_edge("tool", "agent")
    builder.add_edge("data", "decision")
    builder.add_edge("decision", "llm_response")
    builder.add_edge("llm_response", END)

    return builder.compile()
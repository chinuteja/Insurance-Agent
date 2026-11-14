
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.graph.claim_agent_coverage_response import (
    create_claim_coverage_response_node,
)
from app.graph.claim_agent_status_response import (
    create_claim_status_response_node,
)
from app.graph.claim_agent_general import create_claim_general_node
from app.graph.claim_agent_coverage import create_claim_coverage_node
from app.graph.claim_agent_state import ClaimAgentState
from app.graph.claim_agent_status import create_claim_status_node
from app.graph.claim_agent_nodes import create_claim_agent_node
from app.graph.claim_agent_intent import create_claim_intent_node
from app.graph.claim_agent_intent_router import route_after_intent
from app.graph.claim_agent_data import create_claim_data_node
from app.graph.llm_tool_nodes import create_llm_tool_node
from app.graph.llm_agent_router import route_after_llm
from app.graph.claim_agent_decision import create_claim_decision_node
from app.graph.claim_agent_llm_response import create_claim_llm_response_node

from app.graph.document_verification_node import (
    create_document_verification_node,
)

from app.graph.fraud_detection_node import (
    create_fraud_detection_node,
)


def route_after_claim_data(state: ClaimAgentState) -> str:
    """
    Skip document verification when the claim does not exist.
    Otherwise, continue to document verification.
    """

    if state.get("claim") is None:
        return "decision"

    return "document_verification"


def create_claim_agent_graph(db: Session):

    # Create existing nodes
    intent_node = create_claim_intent_node(db)
    status_node = create_claim_status_node(db)
    coverage_node = create_claim_coverage_node(db)
    coverage_response_node = create_claim_coverage_response_node()
    agent_node = create_claim_agent_node(db)
    data_node = create_claim_data_node(db)
    tool_node = create_llm_tool_node(db)
    decision_node = create_claim_decision_node(db)
    llm_response_node = create_claim_llm_response_node(db)
    general_node = create_claim_general_node()
    status_response_node = create_claim_status_response_node()

    # Create document verification node
    document_verification_node = (
        create_document_verification_node(db)
    )

    # Create fraud detection node
    fraud_detection_node = create_fraud_detection_node(db)

    # Initialize graph
    builder = StateGraph(ClaimAgentState)

    # Register nodes
    builder.add_node("intent", intent_node)
    builder.add_node("status", status_node)
    builder.add_node("coverage", coverage_node)
    builder.add_node("agent", agent_node)
    builder.add_node("tool", tool_node)
    builder.add_node("data", data_node)

    builder.add_node(
        "document_verification",
        document_verification_node,
    )

    builder.add_node(
        "fraud_detection",
        fraud_detection_node,
    )

    builder.add_node("decision", decision_node)
    builder.add_node("llm_response", llm_response_node)
    builder.add_node("general", general_node)
    builder.add_node("status_response", status_response_node)
    builder.add_node("coverage_response", coverage_response_node)

    # Entry point
    builder.add_edge(START, "intent")

    # Intent routing
    builder.add_conditional_edges(
        "intent",
        route_after_intent,
        {
            "status": "status",
            "coverage": "coverage",
            "agent": "agent",
            "general": "general",
        },
    )

    # LLM agent routing
    builder.add_conditional_edges(
        "agent",
        route_after_llm,
        {
            "tool": "tool",
            "end": "data",
        },
    )

    # Tool execution loop
    builder.add_edge("tool", "agent")

    # Claim data -> document verification or decision
    builder.add_conditional_edges(
        "data",
        route_after_claim_data,
        {
            "document_verification": "document_verification",
            "decision": "decision",
        },
    )

    # Document verification -> fraud detection
    builder.add_edge(
        "document_verification",
        "fraud_detection",
    )

    # Fraud detection -> claim decision
    builder.add_edge(
        "fraud_detection",
        "decision",
    )

    # Decision -> final LLM response
    builder.add_edge("decision", "llm_response")
    builder.add_edge("llm_response", END)

    # Status flow
    builder.add_edge("status", "status_response")
    builder.add_edge("status_response", END)

    # Coverage flow
    builder.add_edge("coverage", "coverage_response")
    builder.add_edge("coverage_response", END)

    # General insurance questions
    builder.add_edge("general", END)

    return builder.compile()

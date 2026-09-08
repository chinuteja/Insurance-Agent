from langgraph.graph import StateGraph, START, END

from app.graph.claim_state import ClaimState
from app.graph.claim_nodes import create_claim_nodes
from app.graph.claim_policy_nodes import (
    create_policy_node,
    route_after_policy,
)
from app.graph.claim_coverage_nodes import create_coverage_node
from app.graph.claim_document_nodes import create_document_node
from app.graph.claim_decision_nodes import create_decision_node


def create_claim_graph(db):
    claim_node = create_claim_nodes(db)
    policy_node = create_policy_node(db)
    coverage_node = create_coverage_node(db)
    document_node = create_document_node(db)
    decision_node = create_decision_node()

    builder = StateGraph(ClaimState)

    builder.add_node("get_claim", claim_node)
    builder.add_node("check_policy", policy_node)
    builder.add_node("check_coverage", coverage_node)
    builder.add_node("check_documents", document_node)
    builder.add_node("make_decision", decision_node)

    builder.add_edge(START, "get_claim")
    builder.add_edge("get_claim", "check_policy")

    builder.add_conditional_edges(
        "check_policy",
        route_after_policy,
        {
            "check_coverage": "check_coverage",
            "make_decision": "make_decision",
        },
    )

    builder.add_edge("check_coverage", "check_documents")
    builder.add_edge("check_documents", "make_decision")
    builder.add_edge("make_decision", END)

    return builder.compile()
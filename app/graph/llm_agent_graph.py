from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, START, END

from app.graph.llm_agent_state import LLMAgentState
from app.graph.llm_agent_nodes import create_llm_agent_node
from app.graph.llm_tool_nodes import create_llm_tool_node
from app.graph.llm_agent_router import route_after_llm
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="langchain_core")

def create_llm_agent_graph(db: Session):

    llm_node = create_llm_agent_node(db)
    tool_node = create_llm_tool_node(db)

    builder = StateGraph(LLMAgentState)

    builder.add_node("llm", llm_node)
    builder.add_node("tool", tool_node)

    builder.add_edge(START, "llm")

    builder.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tool": "tool",
            "end": END,
        },
    )

    builder.add_edge("tool", "llm")

    return builder.compile()
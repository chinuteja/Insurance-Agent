from langgraph.graph import StateGraph, START, END

from app.graph.state import SimpleState
from app.graph.nodes import hello_node


builder = StateGraph(SimpleState)

builder.add_node("hello", hello_node)

builder.add_edge(START, "hello")
builder.add_edge("hello", END)

graph = builder.compile()
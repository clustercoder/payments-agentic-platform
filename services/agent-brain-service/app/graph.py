from langgraph.graph import StateGraph, END
from app.schemas import AgentState
from app.nodes.observer import observer_node
from app.nodes.reasoning import reasoning_node
from app.nodes.policy import policy_node
from app.nodes.decision import decision_node
from app.nodes.explain import explain_node

graph = StateGraph(AgentState)

# Add Nodes
graph.add_node("observe", observer_node)
graph.add_node("reason", reasoning_node)
graph.add_node("policy", policy_node)
graph.add_node("decide", decision_node)
graph.add_node("explain", explain_node)

# Define Edges
graph.set_entry_point("observe")
graph.add_edge("observe", "reason")
graph.add_edge("reason", "policy")
graph.add_edge("policy", "decide")
graph.add_edge("decide", "explain")
graph.add_edge("explain", END)

agent = graph.compile()
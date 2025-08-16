from langgraph.graph import StateGraph, END
from state import AgentState
from planner_agent import plan_step
from orchestrator import router_node
from summarizer import summarize_node

def should_continue(state):
    return state["should_continue"]

workflow = StateGraph(AgentState)

workflow.add_node("planner", plan_step)
workflow.add_node("execute_step", router_node)
workflow.add_node("summarize", summarize_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "execute_step")
workflow.add_conditional_edges("execute_step", should_continue, {
    "continue": "execute_step",
    "end": "summarize"
})
workflow.add_edge("summarize", END)

app = workflow.compile()
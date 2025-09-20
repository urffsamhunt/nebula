# graph/workflow.py
from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph import nodes

def create_workflow():
    """Creates the LangGraph workflow."""
    workflow = StateGraph(GraphState)

    # Define the nodes
    workflow.add_node("extract_text", nodes.extract_text)
    workflow.add_node("normalize_texts", nodes.normalize_texts)
    workflow.add_node("run_comparisons", nodes.run_comparisons)
    workflow.add_node("aggregate_results", nodes.aggregate_results)

    # Define the edges (the sequence of steps)
    workflow.set_entry_point("extract_text")
    workflow.add_edge("extract_text", "normalize_texts")
    workflow.add_edge("normalize_texts", "run_comparisons")
    workflow.add_edge("run_comparisons", "aggregate_results")
    workflow.add_edge("aggregate_results", END)

    # Compile the workflow into a runnable app
    app = workflow.compile()
    return app

# Create a single instance of the app to be used by the API
graph_app = create_workflow()
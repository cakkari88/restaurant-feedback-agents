"""LangGraph workflow for the restaurant feedback capstone."""
from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from agents import (
    retrieval_agent, analysis_agent, classification_agent,
    recurring_issue_agent, response_drafting_agent, management_review_agent,
    make_llm
)

class FeedbackState(TypedDict, total=False):
    limit: int
    review_text: str
    llm: Any
    reviews: list
    analyses: list
    classified: list
    issue_summary: dict
    drafts: list
    approved_output: dict
    events: list

def build_graph(model: str = "gemma4:e4b", base_url: str = "http://localhost:11434"):
    llm = make_llm(model=model, base_url=base_url)
    def init(state):
        return {"llm": llm, "events": []}
    workflow = StateGraph(FeedbackState)
    workflow.add_node("initialize", init)
    workflow.add_node("retrieval", retrieval_agent)
    workflow.add_node("analysis", analysis_agent)
    workflow.add_node("classification", classification_agent)
    workflow.add_node("recurring_issues", recurring_issue_agent)
    workflow.add_node("draft_responses", response_drafting_agent)
    workflow.add_node("management_review", management_review_agent)
    workflow.add_edge(START, "initialize")
    workflow.add_edge("initialize", "retrieval")
    workflow.add_edge("retrieval", "analysis")
    workflow.add_edge("analysis", "classification")
    workflow.add_edge("classification", "recurring_issues")
    workflow.add_edge("recurring_issues", "draft_responses")
    workflow.add_edge("draft_responses", "management_review")
    workflow.add_edge("management_review", END)
    return workflow.compile()

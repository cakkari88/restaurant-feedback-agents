"""Fast tests that do not call Ollama; run with: pytest -q"""
from agents import retrieval_agent, recurring_issue_agent, management_review_agent

def test_retrieval_loads_sample_reviews():
    result = retrieval_agent({"limit": 3, "events": []})
    assert len(result["reviews"]) == 3
    assert result["reviews"][0]["customer_text"]
    assert "retrieval_agent" in result["events"]

def test_manual_review_overrides_sample_data():
    result = retrieval_agent({"review_text": "Service was slow", "limit": 1, "events": []})
    assert len(result["reviews"]) == 1
    assert result["reviews"][0]["customer_text"] == "Service was slow"

def test_recurring_issue_requires_at_least_two_negative_or_mixed_reviews():
    rows = [
        {"category": "service", "sentiment": "negative"},
        {"category": "service", "sentiment": "mixed"},
        {"category": "food_quality", "sentiment": "positive"},
    ]
    result = recurring_issue_agent({"classified": rows, "events": []})
    issues = result["issue_summary"]["recurring_issues"]
    assert any(x["category"] == "service" and x["count"] == 2 for x in issues)
    assert not any(x["category"] == "food_quality" for x in issues)

def test_management_gate_never_auto_approves():
    result = management_review_agent({
        "drafts": [{"draft_reply": "Thank you for the feedback."}],
        "issue_summary": {}, "events": []
    })
    assert result["approved_output"]["status"] == "DRAFTS_ONLY_HUMAN_APPROVAL_REQUIRED"
    assert result["approved_output"]["drafts"][0]["needs_review"] is True

def test_management_gate_flags_risky_claims():
    result = management_review_agent({
        "drafts": [{"draft_reply": "We have refunded your order."}],
        "issue_summary": {}, "events": []
    })
    assert result["approved_output"]["drafts"][0]["safety_flag"] is True

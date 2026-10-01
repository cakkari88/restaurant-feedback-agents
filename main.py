"""Run the restaurant feedback multi-agent system from a Windows terminal."""
import json
import os
from dotenv import load_dotenv
from graph import build_graph

def main():
    load_dotenv()
    model = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    print("Restaurant Customer Feedback Multi-Agent System")
    print(f"Model: {model}")
    print("Choose: [1] Analyze sample CSV reviews  [2] Analyze one review")
    choice = input("> ").strip()
    if choice == "2":
        review = input("Paste one customer review (max 5000 characters): ").strip()[:5000]
        if not review:
            print("Empty review. Nothing to analyze.")
            return
        initial = {"review_text": review, "limit": 1}
    else:
        raw_limit = input("How many sample reviews? (1-10, default 10): ").strip()
        try:
            limit = max(1, min(int(raw_limit or "10"), 10))
        except ValueError:
            limit = 10
        initial = {"limit": limit}
    app = build_graph(model=model, base_url=base_url)
    try:
        result = app.invoke(initial)
    except Exception as exc:
        print("\nThe workflow could not finish.")
        print(f"Error: {type(exc).__name__}: {exc}")
        print("Check that Ollama is running and that the model has been pulled.")
        return
    output = result.get("approved_output", {})
    print("\n=== RESULTS (DRAFTS ONLY — HUMAN APPROVAL REQUIRED) ===")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print("\nNo reply has been published or sent. Review every draft before use.")

if __name__ == "__main__":
    main()

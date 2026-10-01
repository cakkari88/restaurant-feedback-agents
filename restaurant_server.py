"""MCP server exposing local restaurant feedback tools.

Run with: python restaurant_server.py
The server uses a local CSV and SQLite database. It does not publish reviews online.
"""
import csv
import json
import sqlite3
from pathlib import Path
from collections import Counter
from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "feedback.csv"
DB_PATH = ROOT / "feedback.db"

mcp = FastMCP("restaurant-feedback-tools")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feedback_id TEXT NOT NULL,
            customer_text TEXT NOT NULL,
            sentiment TEXT,
            category TEXT,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


@mcp.tool()
def retrieve_feedback(limit: int = 50) -> str:
    """Retrieve up to 100 sample customer reviews from feedback.csv."""
    limit = max(1, min(int(limit), 100))
    if not CSV_PATH.exists():
        return json.dumps({"error": "feedback.csv was not found"})
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return json.dumps(rows[:limit], ensure_ascii=False)


@mcp.tool()
def save_feedback_analysis(feedback_id: str, customer_text: str, sentiment: str,
                           category: str, summary: str) -> str:
    """Save one analysis record to local SQLite history."""
    allowed_sentiments = {"positive", "negative", "mixed", "neutral", "uncertain"}
    allowed_categories = {"food_quality", "service", "cleanliness", "price",
                          "atmosphere", "other", "uncertain"}
    sentiment = sentiment.strip().lower()
    category = category.strip().lower()
    if sentiment not in allowed_sentiments:
        return json.dumps({"saved": False, "error": "Invalid sentiment"})
    if category not in allowed_categories:
        return json.dumps({"saved": False, "error": "Invalid category"})
    if not customer_text.strip() or len(customer_text) > 5000:
        return json.dumps({"saved": False, "error": "Review must be 1-5000 characters"})
    with _connect() as conn:
        conn.execute(
            "INSERT INTO analyses (feedback_id, customer_text, sentiment, category, summary) VALUES (?, ?, ?, ?, ?)",
            (str(feedback_id)[:100], customer_text[:5000], sentiment, category, summary[:2000])
        )
    return json.dumps({"saved": True, "feedback_id": str(feedback_id)})


@mcp.tool()
def search_feedback_history(query: str = "", limit: int = 20) -> str:
    """Search previously saved analyses by review text, category, sentiment, or summary."""
    limit = max(1, min(int(limit), 100))
    q = f"%{query.strip()[:100]}%"
    with _connect() as conn:
        rows = conn.execute("""
            SELECT feedback_id, customer_text, sentiment, category, summary, created_at
            FROM analyses
            WHERE customer_text LIKE ? OR category LIKE ? OR sentiment LIKE ? OR summary LIKE ?
            ORDER BY id DESC LIMIT ?
        """, (q, q, q, q, limit)).fetchall()
    return json.dumps([dict(r) for r in rows], ensure_ascii=False)


@mcp.tool()
def calculate_feedback_statistics() -> str:
    """Calculate counts by sentiment and category from saved analysis history."""
    with _connect() as conn:
        rows = conn.execute("SELECT sentiment, category FROM analyses").fetchall()
    sentiments = Counter(r["sentiment"] for r in rows)
    categories = Counter(r["category"] for r in rows)
    return json.dumps({
        "total_saved_analyses": len(rows),
        "sentiment_counts": dict(sentiments),
        "category_counts": dict(categories)
    }, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()

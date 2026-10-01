"""Small MCP client used by the LangGraph workflow."""

import asyncio
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def _call_tool(tool_name: str, arguments: dict) -> str:
    """Launch the MCP server and call one tool through stdio."""

    server_params = StdioServerParameters(
        command="python",
        args=["restaurant_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            for content in result.content:
                if getattr(content, "type", None) == "text":
                    return content.text

            raise RuntimeError(f"MCP tool '{tool_name}' returned no text result")


def call_tool(tool_name: str, arguments: dict) -> str:
    """Synchronous wrapper for the MCP tool call."""
    return asyncio.run(_call_tool(tool_name, arguments))


def retrieve_feedback(limit: int = 10) -> list:
    """Retrieve restaurant feedback through MCP."""
    result = call_tool(
        "retrieve_feedback",
        {"limit": limit},
    )

    data = json.loads(result)

    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(data["error"])

    return data

def save_feedback_analysis(
    feedback_id: str,
    customer_text: str,
    sentiment: str,
    category: str,
    summary: str,
) -> dict:
    """Save one analyzed review through MCP."""

    result = call_tool(
        "save_feedback_analysis",
        {
            "feedback_id": feedback_id,
            "customer_text": customer_text,
            "sentiment": sentiment,
            "category": category,
            "summary": summary,
        },
    )

    return json.loads(result)


def search_feedback_history(query: str = "", limit: int = 20) -> list:
    """Search historical analyses through MCP."""

    result = call_tool(
        "search_feedback_history",
        {
            "query": query,
            "limit": limit,
        },
    )

    return json.loads(result)


def calculate_feedback_statistics() -> dict:
    """Calculate historical feedback statistics through MCP."""

    result = call_tool(
        "calculate_feedback_statistics",
        {},
    )

    return json.loads(result)
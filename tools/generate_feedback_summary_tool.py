# tools/generate_feedback_summary_tool.py
"""
Tool: generate_feedback_summary_tool
Lightweight summary tool — replace with LLM later for richer summaries.
"""

from crewai.tools import tool
from typing import Iterable

def _generate_feedback_summary(feedback_data: Iterable) -> str:
    """
    Accepts:
      - feedback_data: list of strings (or dicts with 'text') representing feedback entries.

    Returns:
      - a concise summary string
    """
    # Normalize inputs to strings
    items = []
    if feedback_data is None:
        return "No feedback data provided."

    try:
        for entry in feedback_data:
            if isinstance(entry, dict):
                text = entry.get("text", "")
            else:
                text = str(entry)
            text = text.strip()
            if text:
                items.append(text)
    except TypeError:
        # If a single string was provided rather than list
        text = str(feedback_data).strip()
        if text:
            items = [text]

    if not items:
        return "No valid feedback entries."

    # Simple heuristics: take top 3 entries and join
    top = items[:3]
    joined = " | ".join(top)
    if len(joined) > 800:
        joined = joined[:797] + "..."

    summary = f"Feedback Summary (top {len(top)}): {joined}"
    return summary

# create tool instance (pattern that matches earlier test usage)
generate_feedback_summary_tool = tool("generate_feedback_summary_tool")(_generate_feedback_summary)

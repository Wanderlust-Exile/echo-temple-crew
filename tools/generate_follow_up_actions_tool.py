# tools/generate_follow_up_actions_tool.py
"""
Tool: generate_follow_up_actions_tool
Creates prioritized follow-up actions from a summary and sentiment text input.
"""

from crewai.tools import tool
from typing import Tuple

def _generate_follow_up_actions(input_a, input_b=None) -> str:
    """
    Accepts either:
      - (_summary_string_, _sentiment_string_)
    or
      - (a single dict-like object) with keys {'summary','sentiment'}.

    Returns:
      - a newline-separated action plan string
    """
    # normalize inputs
    if isinstance(input_a, dict) and input_b is None:
        summary = input_a.get("summary", "")
        sentiment = input_a.get("sentiment", "")
    else:
        summary = str(input_a or "")
        sentiment = str(input_b or "")

    sentiment_label = "Neutral"
    if sentiment:
        sentiment_label = sentiment.split(":")[0].strip().capitalize()

    actions = []
    if "Negative" in sentiment_label:
        actions.append("1) Immediately assign a staff member to address major concerns raised.")
        actions.append("2) Offer resolution or concession where appropriate to rebuild trust.")
        actions.append("3) Log detailed issue into knowledge base for root-cause analysis.")
    elif "Positive" in sentiment_label:
        actions.append("1) Follow up with thankful outreach and request for testimonial.")
        actions.append("2) Identify high-engagement leads for next-step conversion outreach.")
    else:
        actions.append("1) Request more detail from neutral responses to clarify intent.")
        actions.append("2) Monitor for patterns over the next campaign cycle.")

    # A generic action that always makes sense
    actions.append("Final) Incorporate feedback into next campaign brief and update outreach templates.")

    out = f"Sentiment: {sentiment_label}\nSummary: {summary}\n\nRecommended Actions:\n" + "\n".join(actions)
    return out

generate_follow_up_actions_tool = tool("generate_follow_up_actions_tool")(_generate_follow_up_actions)

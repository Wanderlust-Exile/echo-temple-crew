# tools/generate_sentiment_analysis_tool.py
"""
Tool: generate_sentiment_analysis_tool
Rule-based sentiment detection (replaceable by LLM or NLP lib later).
"""

from crewai.tools import tool

POSITIVE = ["good", "great", "excellent", "amazing", "positive", "love", "wonderful", "clean"]
NEGATIVE = ["bad", "poor", "terrible", "hate", "awful", "dirty", "noisy", "delay", "slow"]

def _generate_sentiment_analysis(feedback_summary: str) -> str:
    """
    Args:
      - feedback_summary: short text (output of the summary tool)

    Returns:
      - string like "Positive: explanation...", "Negative: explanation...", or "Neutral: explanation..."
    """
    if not feedback_summary:
        return "Neutral: no content to evaluate"

    text = feedback_summary.lower()

    pos_score = sum(text.count(w) for w in POSITIVE)
    neg_score = sum(text.count(w) for w in NEGATIVE)

    if pos_score > neg_score:
        label = "Positive"
        reason = f"Detected {pos_score} positive tokens vs {neg_score} negative tokens."
    elif neg_score > pos_score:
        label = "Negative"
        reason = f"Detected {neg_score} negative tokens vs {pos_score} positive tokens."
    else:
        label = "Neutral"
        reason = f"No clear positive/negative dominance ({pos_score} pos / {neg_score} neg)."

    return f"{label}: {reason}"

generate_sentiment_analysis_tool = tool("generate_sentiment_analysis_tool")(_generate_sentiment_analysis)

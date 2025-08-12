from crewai.tools import tool

@tool("generate_campaign_report_tool")
def generate_campaign_report_tool(summary: str, sentiment: str, actions: str) -> str:
    """Generates a full campaign performance and feedback report."""
    return (
        "=== Campaign Feedback Report ===\n\n"
        f"Summary:\n{summary}\n\n"
        f"Sentiment Analysis:\n{sentiment}\n\n"
        f"Recommended Actions:\n{actions}\n"
    )

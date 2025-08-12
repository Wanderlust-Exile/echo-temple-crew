from crewai import Agent
from tools.generate_feedback_summary_tool import generate_feedback_summary_tool

feedback_summary_agent = Agent(
    role="Feedback Summary Specialist",
    goal="Summarize customer feedback into a concise, actionable overview.",
    backstory=(
        "You are an expert at distilling large amounts of raw feedback "
        "into clear, easy-to-digest summaries that highlight recurring themes."
    ),
    tools=[generate_feedback_summary_tool],
    verbose=True
)

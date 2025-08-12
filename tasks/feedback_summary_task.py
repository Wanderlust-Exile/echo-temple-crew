from crewai import Task
from agents.feedback_summary_agent import feedback_summary_agent

feedback_summary_task = Task(
    description=(
        "Review the provided customer feedback data and produce a clear, concise summary "
        "highlighting the key points and recurring themes."
    ),
    expected_output="A well-structured summary of feedback points.",
    agent=feedback_summary_agent
)

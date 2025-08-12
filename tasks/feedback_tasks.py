# tasks/feedback_tasks.py
"""
Task wrappers for the feedback pipeline.
Each Task wraps a single tool (summary -> sentiment -> follow-up actions).
A chained list `feedback_analysis_chain` is provided for easy inclusion in the Crew.
"""

from crewai import Task
from tools.generate_feedback_summary_tool import generate_feedback_summary_tool
from tools.generate_sentiment_analysis_tool import generate_sentiment_analysis_tool
from tools.generate_follow_up_actions_tool import generate_follow_up_actions_tool

# 1) Summarize raw feedback into a concise digest
generate_feedback_summary_task = Task(
    name="Generate Feedback Summary Task",
    description="Summarize raw feedback into concise, prioritized points.",
    tool=generate_feedback_summary_tool,
    expected_output="A short, structured summary string describing the most important feedback themes."
)

# 2) Analyze sentiment of the summary
generate_sentiment_analysis_task = Task(
    name="Generate Sentiment Analysis Task",
    description="Analyze the feedback summary for sentiment (Positive / Negative / Neutral).",
    tool=generate_sentiment_analysis_tool,
    expected_output="A sentiment label and short reasoning text."
)

# 3) Generate follow-up actions based on summary + sentiment
generate_follow_up_actions_task = Task(
    name="Generate Follow-Up Actions Task",
    description="Produce concrete follow-up actions derived from the summary and sentiment.",
    tool=generate_follow_up_actions_tool,
    expected_output="A bullet list of prioritized follow-up actions."
)

# Chain for convenience: run these in order in your crew/workflow
feedback_analysis_chain = [
    generate_feedback_summary_task,
    generate_sentiment_analysis_task,
    generate_follow_up_actions_task,
]

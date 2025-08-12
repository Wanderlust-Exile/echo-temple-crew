from crewai import Task
from agents.sentiment_analysis_agent import sentiment_analysis_agent

sentiment_analysis_task = Task(
    description=(
        "Analyze the feedback summary and determine the overall sentiment "
        "(positive, negative, mixed), with a brief explanation of the reasoning."
    ),
    expected_output="Sentiment classification and reasoning.",
    agent=sentiment_analysis_agent
)

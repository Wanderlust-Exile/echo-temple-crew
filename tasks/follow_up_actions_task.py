from crewai import Task
from agents.follow_up_actions_agent import follow_up_actions_agent

follow_up_actions_task = Task(
    description=(
        "Using the sentiment analysis, recommend a set of clear follow-up actions "
        "to improve customer satisfaction or leverage positive feedback."
    ),
    expected_output="List of recommended follow-up actions with justification.",
    agent=follow_up_actions_agent
)

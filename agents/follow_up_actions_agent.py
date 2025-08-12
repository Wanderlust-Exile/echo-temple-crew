from crewai import Agent
from tools.generate_follow_up_actions_tool import generate_follow_up_actions_tool

follow_up_actions_agent = Agent(
    role="Follow-Up Strategy Advisor",
    goal="Recommend targeted actions based on sentiment analysis.",
    backstory=(
        "You are a customer success strategist who turns sentiment insights "
        "into actionable steps for outreach, retention, and upselling."
    ),
    tools=[generate_follow_up_actions_tool],
    verbose=True
)

from crewai import Agent
from tools.generate_sentiment_analysis_tool import generate_sentiment_analysis_tool

sentiment_analysis_agent = Agent(
    role="Sentiment Analysis Expert",
    goal="Analyze summarized feedback to determine customer sentiment and reasoning.",
    backstory=(
        "You are a market research analyst specializing in tone and sentiment "
        "extraction from feedback. You identify emotions, trends, and polarity."
    ),
    tools=[generate_sentiment_analysis_tool],
    verbose=True
)

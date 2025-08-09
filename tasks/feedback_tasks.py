from crewai.tools import tool

# --- Tool Definitions ---

def _collect_user_feedback() -> str:
    """Collects raw feedback from users."""
    return input("Please enter the user's feedback: ")

collect_user_feedback = tool("collect_user_feedback")(_collect_user_feedback)


def _analyze_sentiment(feedback: str) -> str:
    """Analyzes sentiment of the feedback."""
    if any(word in feedback.lower() for word in ["bad", "terrible", "poor", "dirty", "loud"]):
        return "Negative"
    elif any(word in feedback.lower() for word in ["great", "amazing", "beautiful", "clean", "wonderful"]):
        return "Positive"
    else:
        return "Neutral"

analyze_sentiment = tool("analyze_sentiment")(_analyze_sentiment)


def _summarize_feedback(feedback: str) -> str:
    """Summarizes key points from the feedback."""
    return f"Summary: {feedback[:100]}..."  # Simple truncation for now

summarize_feedback = tool("summarize_feedback")(_summarize_feedback)


def _recommend_actions(summary: str, sentiment: str) -> str:
    """Recommends actions based on summary and sentiment."""
    if sentiment == "Negative":
        return "Recommended Action: Address cleanliness and noise concerns."
    elif sentiment == "Positive":
        return "Recommended Action: Continue current operations and share testimonials."
    else:
        return "Recommended Action: Gather more data or follow up with customer."

recommend_actions = tool("recommend_actions")(_recommend_actions)

# --- Manual Test Runner ---

if __name__ == "__main__":
    feedback = collect_user_feedback.run()
    print(f"\nCollected Feedback:\n{feedback}")

    sentiment = analyze_sentiment.run(feedback)
    print(f"\nSentiment Analysis:\n{sentiment}")

    summary = summarize_feedback.run(feedback)
    print(f"\nFeedback Summary:\n{summary}")

    actions = recommend_actions.run(summary, sentiment)
    print(f"\nRecommended Actions:\n{actions}")

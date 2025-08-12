# main.py
from crewai import Crew, Agent
from tasks import (
    build_semantic_index,
    cost_monitor_task,
    feedback_summary_task,
    feedback_tasks,
    follow_up_actions_task,
    generate_leads,
    lead_scraper_task,
    optimize_code_task,
    send_emails,
    sentiment_analysis_task,
    simulate_upcoming_campaign,
    update_calendar,
    update_docs,
    write_email_task,
    write_training_notes_task
)
from tools import (
    cost_monitor_tool,
    email_writer_tool,
    generate_campaign_report_tool,
    generate_feedback_summary_tool,
    generate_follow_up_actions_tool,
    generate_sentiment_analysis_tool,
    google_sheets_interface,
    lead_scraper_tool,
    semantic_memory_tool,
    write_training_notes_tool
)

def main():
    # Define agents here (placeholder for your custom agents)
    agent = Agent(name="Main Agent", role="Coordinator")

    # Create the Crew
    crew = Crew(
        agents=[agent],
        tasks=[
            build_semantic_index,
            cost_monitor_task,
            feedback_summary_task,
            feedback_tasks,
            follow_up_actions_task,
            generate_leads,
            lead_scraper_task,
            optimize_code_task,
            send_emails,
            sentiment_analysis_task,
            simulate_upcoming_campaign,
            update_calendar,
            update_docs,
            write_email_task,
            write_training_notes_task
        ],
        tools=[
            cost_monitor_tool,
            email_writer_tool,
            generate_campaign_report_tool,
            generate_feedback_summary_tool,
            generate_follow_up_actions_tool,
            generate_sentiment_analysis_tool,
            google_sheets_interface,
            lead_scraper_tool,
            semantic_memory_tool,
            write_training_notes_tool
        ]
    )

    # Kick things off
    result = crew.kickoff()
    print("Crew execution result:", result)

if __name__ == "__main__":
    main()

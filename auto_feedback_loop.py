import time
import schedule
from crewai import Crew
from agents.feedback_synthesizer import feedback_synthesizer
from tasks.feedback_tasks import generate_campaign_report_tool
from datetime import datetime
import os

# Optional output logging
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_feedback_cycle():
    print(f"\n🔁 Running Feedback Cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Define the task
    from crewai import Task
    task = Task(
        description="Analyze the latest outreach campaign data and generate a performance feedback report. Include conversion metrics and actionables.",
        agent=feedback_synthesizer,
        tools=[generate_campaign_report_tool],
        expected_output="A structured feedback report on the outreach campaign performance."
    )

    # Run the crew with the single agent and task
    crew = Crew(
        agents=[feedback_synthesizer],
        tasks=[task],
        verbose=True
    )

    result = crew.run()

    # Save to outputs with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"{OUTPUT_DIR}/feedback_report_{timestamp}.txt", "w", encoding="utf-8") as f:
        f.write(result)

    print("✅ Feedback cycle complete and saved.\n")

# Schedule it to run every hour (customize as needed)
schedule.every(3).hours.do(run_feedback_cycle)

print("🧠 Feedback Synthesizer Scheduler is now running...")

# Loop forever
while True:
    schedule.run_pending()
    time.sleep(10)

import importlib.util
import sys
import os
from crewai import Crew

# Add project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# === Agents ===
strategist = importlib.import_module("agents.strategist").strategist
researcher = importlib.import_module("agents.researcher").researcher
outreach_agent = importlib.import_module("agents.outreach").outreach_agent
scheduler = importlib.import_module("agents.scheduler").scheduler
archivist = importlib.import_module("agents.archivist").archivist
feedback_synthesizer = importlib.import_module("agents.feedback_synthesizer").feedback_synthesizer
system_optimizer = importlib.import_module("agents.system_optimizer").system_optimizer

# === Tasks ===
leads_task = importlib.import_module("tasks.generate_leads").task
write_emails_task = importlib.import_module("tasks.write_email_task").task
send_emails_task = importlib.import_module("tasks.send_emails").task
calendar_task = importlib.import_module("tasks.update_calendar").task
docs_task = importlib.import_module("tasks.update_docs").task
feedback_analysis_task = importlib.import_module("tasks.feedback_analysis").task
simulate_upcoming_campaigns_task = importlib.import_module("tasks.simulate_upcoming_campaigns").task
analyze_feedback_and_optimize_task = importlib.import_module("tasks.analyze_feedback_and_optimize").task
lead_scraper_task = importlib.import_module("tasks.lead_scraper_task").task
write_training_notes_task = importlib.import_module("tasks.write_training_notes_task").task
optimize_code_task = importlib.import_module("tasks.optimize_code_task").task
cost_monitor_task = importlib.import_module("tasks.cost_monitor_task").task

# === Feedback Synthesizer's tools ===
feedback_tasks = importlib.import_module("tasks.feedback_tasks")
generate_campaign_report_task = feedback_tasks.generate_campaign_report_tool
log_to_google_sheet_task = feedback_tasks.log_to_google_sheet_tool
distribute_training_notes_task = feedback_tasks.distribute_training_notes_tool
trigger_script_updates_task = feedback_tasks.trigger_script_updates_tool
store_structured_insights_task = feedback_tasks.store_structured_insights_tool

# === New Tools ===
from tools.lead_scraper_tool import scrape_leads_tool
from tools.email_writer_tool import write_email_tool
from tools import query_leads  # Semantic memory query tool

# === Assign Tools to Specific Agents ===
researcher.tools = [scrape_leads_tool]
outreach_agent.tools = [write_email_tool]

# === Build Crew ===
crew = Crew(
    agents=[
        strategist,
        researcher,
        outreach_agent,
        scheduler,
        archivist,
        feedback_synthesizer,
        system_optimizer
    ],
    tasks=[
        leads_task,
        write_emails_task,
        send_emails_task,
        calendar_task,
        docs_task,
        feedback_analysis_task,
        simulate_upcoming_campaigns_task,
        analyze_feedback_and_optimize_task,
        optimize_code_task,
        cost_monitor_task,

        # Feedback tools
        generate_campaign_report_task,
        log_to_google_sheet_task,
        distribute_training_notes_task,
        trigger_script_updates_task,
        store_structured_insights_task
    ],
    verbose=True
)

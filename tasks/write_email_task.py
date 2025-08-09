from crewai import Task
from tools.email_writer_tool import write_email_tool
from agents.outreach import outreach_agent  # Assuming this agent writes emails

task = Task(
    description="Generate personalized outreach emails to the leads scraped by the research agent. Match tone with Echo Temple’s brand.",
    expected_output="A set of email drafts tailored to each lead, ready to be sent.",
    tools=[write_email_tool],
    agent=outreach_agent,
    async_execution=False,
    output_file="outputs/email_drafts.json"
)

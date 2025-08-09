from crewai import Task
from agents.outreach import outreach_agent

task = Task(
    description='Send or queue emails via Gmail API to the identified leads.',
    expected_output='Sent confirmation or draft links for each email.',
    agent=outreach_agent
)

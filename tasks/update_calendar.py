from crewai import Task
from agents.scheduler import scheduler

task = Task(
    description='Add follow-up calls and booking opportunities to the shared Google Calendar.',
    expected_output='List of events added to calendar.',
    agent=scheduler
)

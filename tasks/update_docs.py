from crewai import Task
from agents.archivist import archivist

task = Task(
    description='Log leads, responses, and templates in Google Sheets and Docs.',
    expected_output='Updated links to lead sheet and campaign docs.',
    agent=archivist
)

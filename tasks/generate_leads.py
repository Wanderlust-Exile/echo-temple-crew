from crewai import Task
from agents.researcher import researcher

task = Task(
    description='Scrape and compile 10 new potential leads interested in Echo Temple venue rental.',
    expected_output='A list with name, contact, website, and why they may be interested.',
    agent=researcher
)

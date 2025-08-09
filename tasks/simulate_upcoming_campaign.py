from crewai import Task
from agents.strategist import strategist

task = Task(
    description="Simulate the performance of upcoming outreach campaigns using historical feedback and projected strategy.",
    expected_output="A list of projected KPIs, campaign refinements, and recommendations for maximizing reach and engagement.",
    agent=strategist,
    tools=[],  # You can plug in scenario simulation tools here later if needed
    async_execution=False,
    output_file="outputs/campaign_simulation.txt"
)

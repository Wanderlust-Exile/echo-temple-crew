# tasks/cost_monitor_task.py
from crewai import Task
from tools.cost_monitor_tool import cost_monitor_tool
from agents.strategist import strategist  # your existing strategist agent

task = Task(
    description="Monitor API cost usage and trigger cost-saving measures if needed.",
    expected_output="Cost report and suggested actions.",
    agent=strategist,
    async_execution=False
)

def run_cost_monitor():
    result = cost_monitor_tool.run()
    # parse suggestions and act: for now return the suggestions for human/agent review
    return result

task.run_task = run_cost_monitor

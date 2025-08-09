from crewai import Task
from tools.write_training_notes_tool import write_training_notes_tool
from agents.feedback_synthesizer import feedback_synthesizer

task = Task(
    description="Synthesize key insights from campaign feedback into clear, actionable training notes for the team.",
    expected_output="Formatted training notes highlighting best practices and improvements.",
    tools=[write_training_notes_tool],
    agent=feedback_synthesizer,
    async_execution=False,
    output_file="outputs/training_notes.md"
)

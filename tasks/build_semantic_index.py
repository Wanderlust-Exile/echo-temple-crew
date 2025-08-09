from crewai import Task
from tools.semantic_index_builder import build_index_tool

task = Task(
    description="Builds or updates the semantic search index for stored leads, notes, and docs.",
    expected_output="A fully built semantic vector index stored locally or in the vector DB.",
    tools=[build_index_tool],
    async_execution=False
)

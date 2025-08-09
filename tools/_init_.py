from crewai.tools import tool
from tools.semantic_memory_tool import semantic_query
from .google_sheets_interface import google_sheets_interface


@tool("semantic_memory_tool")
def query_leads(question: str) -> str:
    """Query stored leads in semantic memory using natural language."""
    results = semantic_query(question)
    return str(results)

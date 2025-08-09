from crewai import Task
from tools.lead_scraper_tool import scrape_leads_tool
from agents.researcher import researcher  # Assuming researcher does the scraping

task = Task(
    description="Scrape high-quality leads from online sources for Echo Temple venue bookings. Focus on event planners, agencies, and tour operators.",
    expected_output="A structured list of qualified leads including name, email, website, and company.",
    tools=[scrape_leads_tool],
    agent=researcher,
    async_execution=False,
    output_file="outputs/leads.json"
)

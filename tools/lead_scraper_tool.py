# tools/lead_scraper_tool.py

import os
import re
import requests
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from crewai.tools import tool
from tools.google_sheets_interface import GoogleSheetsInterface

from tools.semantic_memory_tool import semantic_store
from openai import OpenAI

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ===== Helper Functions ===== #

def google_search(query, num_results=5):
    """Uses Google Custom Search API to fetch URLs."""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("[WARN] Google API key or CSE ID missing — skipping API search.")
        return []
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results
    }
    res = requests.get(url, params=params)
    if res.status_code == 200:
        data = res.json()
        return [item['link'] for item in data.get("items", [])]
    else:
        print(f"[ERROR] Google Search API: {res.text}")
        return []

def scrape_with_bsoup(url):
    """Scrape a page with BeautifulSoup to find contact details."""
    try:
        res = requests.get(url, timeout=8)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text()

        emails = list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}", text)))
        phones = list(set(re.findall(r"\+?\d[\d\s().-]{7,}\d", text)))

        return {
            "url": url,
            "emails": emails,
            "phones": phones,
            "raw_text": text[:5000]  # store snippet for context
        }
    except Exception as e:
        print(f"[ERROR] BSoup scrape failed for {url}: {e}")
        return None

def categorize_lead(text_snippet):
    """Use GPT to categorize the lead into type (venue, restaurant, etc.)."""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify the business type in one or two words."},
                {"role": "user", "content": text_snippet}
            ]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[WARN] Classification failed: {e}")
        return "Unknown"

def deduplicate_leads(leads):
    """Remove duplicate leads by email or URL."""
    seen = set()
    unique = []
    for lead in leads:
        key = tuple(sorted(lead.get("emails", []))) + (lead.get("url"),)
        if key not in seen:
            seen.add(key)
            unique.append(lead)
    return unique

# ===== Main Tool Function ===== #

@tool("lead_scraper_tool")
def scrape_leads(query: str) -> str:
    """
    Hybrid lead scraper: Uses Google Search API + BeautifulSoup to gather leads,
    extracts emails & phones, deduplicates, categorizes, and stores in Google Sheet + semantic memory.
    """
    print(f"[INFO] Starting lead scrape for: {query}")

    # Step 1: Search via Google API
    urls = google_search(query)

    # Step 2: Fallback or supplement with BeautifulSoup scraping
    scraped_data = []
    for url in urls:
        data = scrape_with_bsoup(url)
        if data:
            data["category"] = categorize_lead(data["raw_text"])
            scraped_data.append(data)

    # Step 3: Deduplicate
    unique_leads = deduplicate_leads(scraped_data)

    # Step 4: Store in Google Sheet
    upload_to_sheet(unique_leads, SHEET_ID)

    # Step 5: Store in semantic memory
    for lead in unique_leads:
        semantic_store(
            text=f"{lead['url']} | {', '.join(lead['emails'])} | {', '.join(lead['phones'])} | {lead['category']}",
            metadata={"source": lead["url"], "category": lead["category"]}
        )

    print(f"[SUCCESS] {len(unique_leads)} leads scraped and stored.")
    return f"Scraped and stored {len(unique_leads)} leads."


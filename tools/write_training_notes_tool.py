from crewai.tools import tool
from openai import OpenAI
from utils.google_docs_uploader import upload_to_gdoc, fetch_recent_notes  # Ensure these exist
import os
import json
from datetime import datetime
from pathlib import Path

@tool("write_training_notes")
def write_training_notes(data: dict) -> str:
    """
    Generate versioned training notes from feedback/context, inject past memory,
    upload to Google Docs, and log metadata.
    
    Expects:
    {
        "feedback": "string",
        "context": "optional string",
        "campaign_name": "optional string"
    }
    """

    # --- Setup ---
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ Missing OpenAI API key"

    client = OpenAI(api_key=api_key)
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    short_date = now.strftime("%Y-%m-%d")

    campaign = data.get("campaign_name", "General")
    feedback = data.get("feedback", "")
    context = data.get("context", "")

    # --- Memory Injection ---
    past_notes = fetch_recent_notes(limit=2)  # You define this function to pull content from past notes
    past_summary = "\n---\n".join(past_notes) if past_notes else "N/A"

    # --- Prompt ---
    prompt = f"""
You are a senior AI training analyst.

Write clear, structured training notes for a remote outreach team working on marketing for a cultural venue, based on:

- Current Feedback
- Campaign Context
- Memory of Previous Notes

---

📌 Feedback:
{feedback}

📄 Context:
{context or 'N/A'}

🧠 Past Training Notes Memory:
{past_summary}

---

Structure:
- Title
- Summary of Insights
- Bullet List of Key Feedback Points
- 3–5 Actionable Recommendations
- Friendly but professional tone
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    training_notes = response.choices[0].message.content

    # --- GDoc Title & Upload ---
    gdoc_title = f"{campaign} Training Notes - {short_date} ({timestamp})"
    doc_url = upload_to_gdoc(gdoc_title, training_notes)

    # --- Metadata Logging ---
    log_entry = {
        "title": gdoc_title,
        "timestamp": timestamp,
        "campaign": campaign,
        "gdoc_url": doc_url,
        "feedback_snippet": feedback[:250]
    }

    log_path = Path("logs/training_notes_log.json")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    return f"✅ Training notes generated, uploaded, and logged:\n📄 {gdoc_title}\n🔗 {doc_url}"


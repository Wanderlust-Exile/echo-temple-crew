import json
import os
from datetime import datetime

LOG_FILE = os.path.join("logs", "optimizer_decisions.json")

def log_optimizer_decision(agent_name: str, change_summary: str, rationale: str, files_changed: list):
    """Log optimization decisions in a structured JSON file."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent_name,
        "change_summary": change_summary,
        "rationale": rationale,
        "files_changed": files_changed
    }

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

    print(f"[LOG] Optimization decision saved to {LOG_FILE}")

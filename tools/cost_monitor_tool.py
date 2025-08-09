# tools/cost_monitor_tool.py
from crewai.tools import tool
import os
import json
from datetime import datetime, timedelta
from utils.training_db import get_recent_runs

# Basic pricing config (customize)
PRICING = {
    "openai_chat": 0.0003,   # USD per token estimate — set correct values
    "openai_embed": 0.0001
}
# Budget thresholds
BUDGET_MONTHLY_USD = float(os.getenv("BUDGET_MONTHLY_USD", "50.0"))

def estimate_cost_from_runs(runs):
    # Basic heuristic: if run.metrics records tokens or api_cost, use it. Else fallback to naive per-run cost.
    total = 0.0
    for r in runs:
        metrics = json.loads(r.get("metrics") or "{}")
        if "api_cost" in metrics:
            total += float(metrics["api_cost"])
        elif "tokens" in metrics and metrics["type"] == "chat":
            total += metrics["tokens"] * PRICING["openai_chat"]
        else:
            # small fixed cost per run
            total += 0.001
    return total

@tool("cost_monitor_tool")
def cost_monitor_tool(window_days: int = 30) -> str:
    """
    Analyze recent runs and estimate cost. Return suggested actions if threshold exceeded.
    """
    all_runs = get_recent_runs(500)
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    recent = [r for r in all_runs if datetime.fromisoformat(r["timestamp"]) >= cutoff]
    estimated = estimate_cost_from_runs(recent)

    # project monthly
    projected_monthly = (estimated / max(1, window_days)) * 30

    actions = []
    if projected_monthly > BUDGET_MONTHLY_USD:
        actions.append("reduce_model_tier")
        actions.append("decrease_polling_frequency")
        actions.append("batch_requests")
    else:
        actions.append("within_budget")

    return json.dumps({
        "estimated_window_cost": estimated,
        "projected_monthly_cost": projected_monthly,
        "budget_monthly": BUDGET_MONTHLY_USD,
        "suggested_actions": actions
    }, indent=2)

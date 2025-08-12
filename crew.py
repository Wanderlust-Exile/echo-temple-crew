# crew.py (dynamic, robust version)
import os
import sys
import importlib
import traceback

# Add project root to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from crewai import Crew

def _safe_import(module_name):
    """Import module safely and return the module or None on failure."""
    try:
        return importlib.import_module(module_name)
    except Exception:
        print(f"[crew.py] Failed to import {module_name}:\n{traceback.format_exc()}")
        return None

def _collect_objects_from_module(module, suffix):
    """
    Given a module and suffix (e.g. '_agent', '_task', '_tool'), return a dict of
    matching attributes (name -> object).
    """
    found = {}
    if not module:
        return found
    for name in dir(module):
        if name.lower().endswith(suffix):
            try:
                found[name] = getattr(module, name)
            except Exception:
                pass
    return found

# ------------------------------
# Discover agents dynamically
# ------------------------------
agents_dir = os.path.join(project_root, "agents")
agents_map = {}

if os.path.isdir(agents_dir):
    for fn in os.listdir(agents_dir):
        if not fn.endswith(".py"):
            continue
        if fn.startswith("__"):
            continue
        mod_name = fn[:-3]
        full_module = f"agents.{mod_name}"
        mod = _safe_import(full_module)
        # look for any exported variable that ends with '_agent' (common pattern)
        found = _collect_objects_from_module(mod, "_agent")
        # If nothing matching, also try name equal to module (e.g. strategist variable)
        if not found and mod:
            # try common variable names
            for candidate in [mod_name, f"{mod_name}_agent", mod_name.replace("-", "_")]:
                if hasattr(mod, candidate):
                    found[candidate] = getattr(mod, candidate)
        agents_map.update(found)
else:
    print("[crew.py] Warning: agents/ directory not found.")

# ------------------------------
# Discover tasks dynamically
# ------------------------------
tasks_dir = os.path.join(project_root, "tasks")
tasks_map = {}

if os.path.isdir(tasks_dir):
    for fn in os.listdir(tasks_dir):
        if not fn.endswith(".py"):
            continue
        if fn.startswith("__"):
            continue
        mod_name = fn[:-3]
        full_module = f"tasks.{mod_name}"
        mod = _safe_import(full_module)
        # collect attributes ending with '_task' or named 'task'
        if mod:
            found = _collect_objects_from_module(mod, "_task")
            # if no _task names, try a single 'task' attr
            if not found and hasattr(mod, "task"):
                found["task"] = getattr(mod, "task")
            # also try common verbose names: e.g., generate_feedback_summary_task etc.
            tasks_map.update(found)
else:
    print("[crew.py] Warning: tasks/ directory not found.")

# ------------------------------
# Discover tools dynamically
# ------------------------------
tools_dir = os.path.join(project_root, "tools")
tools_map = {}

if os.path.isdir(tools_dir):
    for fn in os.listdir(tools_dir):
        if not fn.endswith(".py"):
            continue
        if fn.startswith("__"):
            continue
        mod_name = fn[:-3]
        full_module = f"tools.{mod_name}"
        mod = _safe_import(full_module)
        if mod:
            found = _collect_objects_from_module(mod, "_tool")
            # check also for attributes ending with 'tool' (in case of different casing)
            for name in dir(mod):
                if name.lower().endswith("tool") and name not in found:
                    try:
                        found[name] = getattr(mod, name)
                    except Exception:
                        pass
            tools_map.update(found)
else:
    print("[crew.py] Warning: tools/ directory not found.")

# ------------------------------
# Build ordered agent list
# ------------------------------
# Prefer a sane order; fallback to whatever was discovered
preferred_agent_order = [
    "strategist",
    "researcher",
    "outreach_agent",
    "outreach",            # fallback names
    "scheduler",
    "archivist",
    "system_optimizer",
    "feedback_summary_agent",
    "sentiment_analysis_agent",
    "follow_up_actions_agent",
    "feedback_collector_agent",
    "feedback_analyzer_agent",
    "feedback_action_agent"
]

agents_list = []
seen = set()
for name in preferred_agent_order:
    if name in agents_map and agents_map[name] not in seen:
        agents_list.append(agents_map[name])
        seen.add(agents_map[name])

# append any remaining discovered agents
for name, obj in agents_map.items():
    if obj not in seen:
        agents_list.append(obj)
        seen.add(obj)

# ------------------------------
# Build ordered tasks list
# ------------------------------
preferred_task_order = [
    "lead_scraper_task",
    "generate_leads_task",
    "leads_task",
    "write_email_task",
    "write_emails_task",
    "send_emails_task",
    "update_calendar_task",
    "update_calendar",
    "calendar_task",
    "update_docs_task",
    "update_docs",
    "build_semantic_index",
    "build_semantic_index_task",
    "feedback_summary_task",
    "generate_feedback_summary_task",
    "sentiment_analysis_task",
    "generate_sentiment_analysis_task",
    "follow_up_actions_task",
    "generate_follow_up_actions_task",
    "simulate_upcoming_campaigns_task",
    "analyze_feedback_and_optimize_task",
    "optimize_code_task",
    "cost_monitor_task"
]

tasks_list = []
seen = set()
# add preferred tasks first if present
for name in preferred_task_order:
    if name in tasks_map and tasks_map[name] not in seen:
        tasks_list.append(tasks_map[name])
        seen.add(tasks_map[name])

# then add remaining discovered tasks
for name, obj in tasks_map.items():
    if obj not in seen:
        tasks_list.append(obj)
        seen.add(obj)

# ------------------------------
# Tool assignments to agents (best-effort)
# ------------------------------
# Assign common tools if they exist
def _assign_tool_to_agent(agent_obj, tool_candidates):
    if not agent_obj:
        return False
    for tname in tool_candidates:
        if tname in tools_map:
            try:
                # try attribute assignment if agent has .tools list, else create it
                existing = getattr(agent_obj, "tools", None)
                if existing is None:
                    setattr(agent_obj, "tools", [tools_map[tname]])
                else:
                    existing.append(tools_map[tname])
                    setattr(agent_obj, "tools", existing)
                return True
            except Exception:
                continue
    return False

# researcher -> lead scraper
if "researcher" in agents_map:
    _assign_tool_to_agent(agents_map.get("researcher"), ["scrape_leads_tool", "lead_scraper_tool", "lead_scraper_tool"])
# outreach -> email writer
if "outreach_agent" in agents_map:
    _assign_tool_to_agent(agents_map.get("outreach_agent"), ["write_email_tool", "email_writer_tool", "email_writer_tool"])
elif "outreach" in agents_map:
    _assign_tool_to_agent(agents_map.get("outreach"), ["write_email_tool", "email_writer_tool"])

# ------------------------------
# Final crew build
# ------------------------------
print("[crew.py] Agents discovered:", list(agents_map.keys()))
print("[crew.py] Tasks discovered:", list(tasks_map.keys()))
print("[crew.py] Tools discovered:", list(tools_map.keys()))

crew = Crew(
    agents=agents_list,
    tasks=tasks_list,
    verbose=True
)

# (Optional) show summary after instantiation
try:
    print("[crew.py] Crew built with", len(agents_list), "agents and", len(tasks_list), "tasks.")
except Exception:
    pass

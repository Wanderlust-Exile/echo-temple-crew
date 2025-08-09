# agents/system_optimizer.py
from crewai import Agent
from utils.training_db import get_recent_runs
from utils.git_ops import create_patch_and_branch
import difflib
import os
import json

system_optimizer = Agent(
    role="System Optimizer - Code & Performance",
    goal="Continuously analyze run logs and code to find safe, high-ROI optimizations, propose patches, and auto-apply low-risk changes with full logging.",
    backstory="MSc in Software Performance Engineering; built self-optimizing pipelines for distributed systems.",
    verbose=True,
    allow_delegation=False
)

# helper methods attached to agent for external invocation
def propose_formatting_patch(file_path: str, new_content: str):
    """Return a patch (dict) ready for git_ops.create_patch_and_branch"""
    return {file_path: new_content}

# attach functions for external import usage
system_optimizer.propose_formatting_patch = propose_formatting_patch
system_optimizer.analyze_recent_runs = lambda limit=50: get_recent_runs(limit)

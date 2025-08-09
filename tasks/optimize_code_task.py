import os
import json
import subprocess
import datetime
import autopep8
from pathlib import Path

# === Config Paths ===
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)
OPTIMIZER_LOG = LOGS_DIR / "optimizer_decisions.json"
CHANGELOG_FILE = BASE_DIR / "CHANGELOG.md"
SEMANTIC_INDEX_SCRIPT = BASE_DIR / "tools" / "semantic_index_builder.py"


def log_optimization(file_path, changes_summary):
    """Append an optimization decision to optimizer_decisions.json"""
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "file": str(file_path),
        "summary": changes_summary
    }

    if OPTIMIZER_LOG.exists():
        with open(OPTIMIZER_LOG, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)
    with open(OPTIMIZER_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def update_changelog(changes_summary):
    """Add an entry to CHANGELOG.md"""
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"\n## [{timestamp}] Optimization\n- {changes_summary}\n"
    with open(CHANGELOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def create_and_commit_branch(branch_name, commit_message):
    """Create a new branch and commit changes"""
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
    except subprocess.CalledProcessError:
        # If branch exists, just switch
        subprocess.run(["git", "checkout", branch_name], check=True)

    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)


def rebuild_semantic_index():
    """Run semantic index rebuild script"""
    subprocess.run(["python", str(SEMANTIC_INDEX_SCRIPT)], check=True)


def optimize_code(file_path):
    """Run code formatting and optimization pipeline"""
    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    # Example optimization: Auto-format with PEP8
    optimized_code = autopep8.fix_code(original_code)

    if optimized_code != original_code:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(optimized_code)

        changes_summary = f"Auto-formatted {file_path.name} to PEP8 standards."
        log_optimization(file_path, changes_summary)
        update_changelog(changes_summary)

        branch_name = f"optimize/{file_path.stem}-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        create_and_commit_branch(branch_name, changes_summary)

        # Trigger semantic index rebuild after a major code change
        rebuild_semantic_index()

        print(f"[Optimizer] {file_path} updated, logged, and committed.")
    else:
        print(f"[Optimizer] No changes required for {file_path}.")


if __name__ == "__main__":
    # Example run: optimize all .py files in tasks/
    tasks_dir = BASE_DIR / "tasks"
    for py_file in tasks_dir.glob("*.py"):
        if py_file.name != Path(__file__).name:  # Skip self
            optimize_code(py_file)

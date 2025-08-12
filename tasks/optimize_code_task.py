import os
import json
import datetime
import subprocess
from utils.semantic_index_builder import rebuild_semantic_index

# ======================
# Logging Functions
# ======================
def log_optimizer_decision(decision_data):
    os.makedirs("logs", exist_ok=True)
    log_path = "logs/optimizer_decisions.json"

    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(decision_data)

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def update_changelog(change_entry):
    changelog_path = "CHANGELOG.md"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"## {timestamp}\n- {change_entry}\n\n"

    if os.path.exists(changelog_path):
        with open(changelog_path, "a", encoding="utf-8") as f:
            f.write(entry)
    else:
        with open(changelog_path, "w", encoding="utf-8") as f:
            f.write("# Changelog\n\n" + entry)

# ======================
# Git Functions
# ======================
def finalize_and_push(commit_message="Automated optimization commit", auto_push=True):
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    branch_name = f"optimize-{timestamp}"

    try:
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)

        if auto_push:
            subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
            print(f"✅ Changes pushed to branch: {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")

# ======================
# Optimization Logic
# ======================
def optimize_code():
    """
    Simulates code optimization.
    Replace this with your real optimization process.
    """
    print("🔧 Optimizing code...")
    # Actual optimization logic would go here
    changes_made = True
    return changes_made

def run():
    print("🚀 Starting code optimization task...")
    changes_made = optimize_code()

    if changes_made:
        decision = {
            "timestamp": datetime.datetime.now().isoformat(),
            "description": "Improved code efficiency in optimize_code_task.py",
            "files_changed": ["tasks/optimize_code_task.py"]
        }
        log_optimizer_decision(decision)
        update_changelog("Improved code efficiency in optimize_code_task.py")

        print("📚 Rebuilding semantic index...")
        try:
            rebuild_semantic_index()
        except Exception as e:
            print(f"⚠️ Semantic index rebuild failed: {e}")

        finalize_and_push("Automated optimization commit", auto_push=True)
    else:
        print("✅ No changes detected. Nothing to commit.")

if __name__ == "__main__":
    run()

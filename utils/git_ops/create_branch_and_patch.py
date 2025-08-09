import subprocess
from datetime import datetime

def create_branch_and_patch(branch_prefix="auto-optimize"):
    """Create a new git branch and commit pending changes."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    branch_name = f"{branch_prefix}_{timestamp}"

    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True)
        subprocess.run(["git", "add", "."], check=True)
        commit_message = f"Automated optimization patch {timestamp}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print(f"[GIT] Created branch '{branch_name}' and committed changes.")
        return branch_name
    except subprocess.CalledProcessError as e:
        print(f"[GIT ERROR] {e}")
        return None

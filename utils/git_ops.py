# utils/git_ops.py
from git import Repo
from pathlib import Path
import tempfile
import os

REPO_PATH = Path(__file__).resolve().parents[1]  # project root
repo = Repo(REPO_PATH)

def create_patch_and_branch(patch_files: dict, branch_name: str = None, commit_msg: str = "Auto optimization"):
    """
    patch_files: dict {relative_path: new_text}
    Creates a branch, writes files, commits, and returns branch name and commit sha.
    """
    if branch_name is None:
        branch_name = f"optimization/{os.getlogin()[:6]}-{int(os.times()[4])}"

    # create branch from current HEAD
    new_branch = repo.create_head(branch_name)
    new_branch.checkout()

    # write files
    for rel_path, content in patch_files.items():
        full = REPO_PATH / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)

    repo.index.add(list(patch_files.keys()))
    commit = repo.index.commit(commit_msg)
    return branch_name, commit.hexsha

def stash_and_restore():
    repo.git.stash("save")
    repo.git.stash("pop")

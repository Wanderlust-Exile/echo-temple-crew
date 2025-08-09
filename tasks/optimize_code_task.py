import os
import json
import subprocess
import datetime
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
import difflib
import shutil

# optional libs: GitPython for finer control (fallback to subprocess if missing)
try:
    from git import Repo, GitCommandError
except Exception:
    Repo = None
    GitCommandError = Exception

try:
    import autopep8
except Exception:
    autopep8 = None

# config
BASE_DIR = Path(__file__).resolve().parents[1]  # repo root
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
OPT_DECISIONS = LOGS_DIR / "optimizer_decisions.json"
OPT_FAILURES = LOGS_DIR / "optimizer_failures.json"
CHANGELOG_FILE = BASE_DIR / "CHANGELOG.md"
SEMANTIC_INDEXER_MODULE = "utils.semantic_index"  # prefer python module call if available
SEMANTIC_INDEX_SCRIPT = BASE_DIR / "tools" / "semantic_index_builder.py"

# safety/config flags (tweak here or set env vars)
DRY_RUN = os.getenv("OPTIMIZER_DRY_RUN", "false").lower() in ("1", "true", "yes")
AUTO_PUSH = os.getenv("OPTIMIZER_AUTO_PUSH", "false").lower() in ("1", "true", "yes")
RUN_TESTS = os.getenv("OPTIMIZER_RUN_TESTS", "true").lower() in ("1", "true", "yes")
AUTO_REBUILD_INDEX = os.getenv("OPTIMIZER_AUTO_REBUILD", "true").lower() in ("1", "true", "yes")
TEST_CMD = os.getenv("OPTIMIZER_TEST_CMD", "pytest -q")  # or your test command


# -------------------------
# Helpers: logging, changelog, git
# -------------------------
def _now_iso():
    return datetime.datetime.utcnow().isoformat() + "Z"


def _read_json(path: Path) -> List[Dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _append_json(path: Path, entry: Dict):
    arr = _read_json(path)
    arr.append(entry)
    path.write_text(json.dumps(arr, indent=2), encoding="utf-8")


def log_decision(entry: Dict):
    _append_json(OPT_DECISIONS, entry)
    print(f"[OPT] Logged decision: {entry.get('summary')}")


def log_failure(entry: Dict):
    _append_json(OPT_FAILURES, entry)
    print(f"[OPT-FAIL] Logged failure: {entry.get('summary')}")


def update_changelog(version_tag: str, summary: str, files_changed: List[str], impact: str):
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    header = f"## [{version_tag}] - {timestamp}\n\n"
    body = f"**Impact:** {impact}\n\n### Changes\n- {summary}\n\n**Files changed:**\n"
    for f in files_changed:
        body += f"- {f}\n"
    body += "\n"
    if not CHANGELOG_FILE.exists():
        CHANGELOG_FILE.write_text("# Changelog\n\n", encoding="utf-8")
    with CHANGELOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(header + body)
    print(f"[CHANGELOG] Appended entry for {version_tag}")


def git_create_branch_and_commit(branch_name: str, commit_msg: str) -> Tuple[bool, str]:
    """
    Creates branch and commits. Returns (success, commit_sha or error).
    """
    if Repo is None:
        # fallback to git CLI
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            subprocess.run(["git", "add", "-A"], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            sha = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
            return True, sha
        except subprocess.CalledProcessError as e:
            return False, str(e)
    else:
        try:
            repo = Repo(str(BASE_DIR))
            # create branch from current HEAD
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            repo.index.add([str(p) for p in BASE_DIR.rglob("*.py")])
            commit = repo.index.commit(commit_msg)
            return True, commit.hexsha
        except GitCommandError as e:
            return False, str(e)


def git_push(branch_name: str) -> Tuple[bool, str]:
    if not AUTO_PUSH:
        return True, "auto_push disabled"
    try:
        if Repo is None:
            subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
        else:
            repo = Repo(str(BASE_DIR))
            origin = repo.remote(name="origin")
            origin.push(refspec=f"{branch_name}:{branch_name}")
        return True, "pushed"
    except Exception as e:
        return False, str(e)


# -------------------------
# Core: format/optimize, diff, impact classification, test, apply
# -------------------------
def format_code_text(src: str) -> str:
    if autopep8:
        try:
            return autopep8.fix_code(src)
        except Exception:
            return src
    # fallback: return original
    return src


def compute_diff_summary(original: str, new: str, max_lines=20) -> Tuple[int, str]:
    diff = list(difflib.unified_diff(original.splitlines(), new.splitlines(), lineterm=""))
    changed_lines = sum(1 for line in diff if line.startswith("+ ") or line.startswith("- "))
    # produce a short diff preview
    preview = "\n".join(diff[:max_lines]) if diff else ""
    return changed_lines, preview


def classify_impact(changed_lines: int) -> str:
    # thresholds are heuristics — tweak as needed
    if changed_lines == 0:
        return "none"
    if changed_lines < 10:
        return "minor"
    if changed_lines < 100:
        return "moderate"
    return "major"


def run_tests() -> Tuple[bool, str]:
    if not RUN_TESTS:
        return True, "Tests disabled"
    try:
        print(f"[TEST] Running tests with: {TEST_CMD}")
        result = subprocess.run(TEST_CMD.split(), cwd=str(BASE_DIR), capture_output=True, text=True, check=False)
        ok = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        return ok, output
    except Exception as e:
        return False, str(e)


def attempt_optimize_file(path: Path) -> Dict:
    """
    Attempt to optimize a single file:
    - read original
    - format
    - compute diff/impact
    - if changes, write to temp, run tests, commit/branch/push and log; rollback if tests fail
    Returns a dict with status/details.
    """
    res = {
        "file": str(path.relative_to(BASE_DIR)),
        "changed": False,
        "impact": "none",
        "changed_lines": 0,
        "commit": None,
        "branch": None,
        "summary": ""
    }

    try:
        original = path.read_text(encoding="utf-8")
    except Exception as e:
        res["summary"] = f"read_error: {e}"
        return res

    new = format_code_text(original)
    changed_lines, preview = compute_diff_summary(original, new)
    impact = classify_impact(changed_lines)

    res.update({"changed_lines": changed_lines, "impact": impact})

    if changed_lines == 0:
        res["summary"] = "no changes"
        return res

    # if dry run, don't persist or commit
    if DRY_RUN:
        res["changed"] = True
        res["summary"] = f"DRY_RUN: would change {changed_lines} lines, impact={impact}"
        return res

    # make a safety copy (for rollback)
    backup_path = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup_path)

    # write new content
    path.write_text(new, encoding="utf-8")

    # run tests
    tests_ok, test_output = run_tests()
    if not tests_ok:
        # rollback
        if backup_path.exists():
            shutil.move(str(backup_path), str(path))
        failure_entry = {
            "timestamp": _now_iso(),
            "file": str(path.relative_to(BASE_DIR)),
            "summary": f"Tests failed after formatting. impact={impact}",
            "test_output": test_output
        }
        log_failure(failure_entry)
        res["summary"] = "tests_failed"
        return res

    # tests succeeded - commit changes
    version_tag = datetime.datetime.utcnow().strftime("auto/%Y%m%d%H%M%S")
    commit_msg = f"Auto-optimization: {path.name} ({impact})"
    branch_name = f"auto-opt/{path.stem}-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    ok, commit_or_err = git_create_branch_and_commit(branch_name, commit_msg)
    if not ok:
        # commit failed - record and rollback
        if backup_path.exists():
            shutil.move(str(backup_path), str(path))
        res["summary"] = f"git_commit_failed: {commit_or_err}"
        return res

    res["changed"] = True
    res["commit"] = commit_or_err
    res["branch"] = branch_name
    res["summary"] = f"changed {changed_lines} lines, impact={impact}"
    # log decision
    dec = {
        "timestamp": _now_iso(),
        "file": str(path.relative_to(BASE_DIR)),
        "summary": res["summary"],
        "preview_diff": preview,
        "commit": res["commit"],
        "branch": res["branch"],
        "impact": impact
    }
    log_decision(dec)

    # optional push
    if AUTO_PUSH:
        pushed, push_msg = git_push(branch_name)
        dec["push_result"] = {"ok": pushed, "msg": push_msg}

    # rebuild semantic index after major changes
    if AUTO_REBUILD_INDEX and impact == "major":
        try:
            # Try calling module function first (if available)
            try:
                import importlib
                mod = importlib.import_module(SEMANTIC_INDEXER_MODULE)
                if hasattr(mod, "build_semantic_index"):
                    mod.build_semantic_index()
                else:
                    # fallback to script
                    subprocess.run(["python", str(SEMANTIC_INDEX_SCRIPT)], check=True)
            except Exception:
                # fallback to script
                subprocess.run(["python", str(SEMANTIC_INDEX_SCRIPT)], check=True)

            dec["index_rebuilt"] = True
        except Exception as e:
            dec["index_rebuilt"] = False
            dec["index_error"] = str(e)

    # update changelog with version tag
    update_changelog(version_tag, res["summary"], [str(path.relative_to(BASE_DIR))], impact)

    # cleanup backup
    if backup_path.exists():
        backup_path.unlink()

    return res


# -------------------------
# Entrypoint function (task runner)
# -------------------------
def run_optimizer_on_paths(paths: List[str] = None) -> Dict:
    """
    Optimize one or many paths. If paths is None, optimize a default candidate set.
    Returns a summary dict.
    """
    if paths is None:
        # Default candidates: all python files under core dirs (safe list)
        candidates = []
        for d in ["tools", "tasks", "agents", "utils"]:
            base = BASE_DIR / d
            if base.exists():
                for p in base.rglob("*.py"):
                    # skip heavy or non-source files
                    if p.name.startswith("_"):
                        continue
                    if "venv" in str(p).lower():
                        continue
                    candidates.append(p)
    else:
        candidates = [Path(p) for p in paths]

    summary = {"runs": [], "timestamp": _now_iso()}

    for p in candidates:
        try:
            r = attempt_optimize_file(p)
            summary["runs"].append(r)
        except Exception as e:
            err_entry = {
                "timestamp": _now_iso(),
                "file": str(p.relative_to(BASE_DIR)),
                "summary": f"exception: {e}"
            }
            log_failure(err_entry)
            summary["runs"].append(err_entry)

    return summary


# Bind a simple Task-like object for Crew integration (lightweight)
class OptimizeCodeTask:
    def __init__(self):
        self.description = "Automated code optimizer (formatting, tests, commit, changelog, index rebuild)"
        self.expected_output = "Summary JSON"
        self.agent = None  # assign to system_optimizer in crew.py if needed

    def run(self, paths: List[str] = None):
        return run_optimizer_on_paths(paths)


# Export a single instance named "task" similar to other tasks
task = OptimizeCodeTask()

# If run as script, run default
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--paths", nargs="+", help="Paths to optimize (optional)")
    parser.add_argument("--dry", action="store_true", help="Dry run (no changes)")
    args = parser.parse_args()
    if args.dry:
        DRY_RUN = True
    res = run_optimizer_on_paths(args.paths)
    print(json.dumps(res, indent=2))

from datetime import datetime
import os

CHANGELOG_FILE = "CHANGELOG.md"

def update_changelog(version: str, description: str, files_changed: list):
    """Append a changelog entry to the CHANGELOG.md file."""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = f"\n## [{version}] - {timestamp}\n\n### Changes\n- {description}\n\n### Files Changed\n" + \
            "\n".join(f"- {file}" for file in files_changed) + "\n"

    if not os.path.exists(CHANGELOG_FILE):
        with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
            f.write("# Changelog\n")
            f.write(entry)
    else:
        with open(CHANGELOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

    print(f"[CHANGELOG] Updated {CHANGELOG_FILE}")

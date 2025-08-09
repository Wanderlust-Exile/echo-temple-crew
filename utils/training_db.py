# utils/training_db.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_PATH = Path("logs/training.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = _get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent TEXT,
        task TEXT,
        inputs TEXT,
        outputs TEXT,
        metrics TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_run(agent: str, task: str, inputs: Dict[str, Any], outputs: Dict[str, Any], metrics: Optional[Dict[str,Any]] = None):
    conn = _get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO runs (agent, task, inputs, outputs, metrics, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (agent, task, json.dumps(inputs, default=str), json.dumps(outputs, default=str), json.dumps(metrics or {}, default=str), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_recent_runs(limit: int = 50) -> List[Dict[str,Any]]:
    conn = _get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# Initialize DB on import
init_db()

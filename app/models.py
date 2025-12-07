import sqlite3
from datetime import datetime
from .config import settings
import os

def _sqlite_path_from_url(url: str) -> str:
    # Accept formats like sqlite:////data/app.db
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "")
    return url

DB_PATH = _sqlite_path_from_url(settings.DATABASE_URL)

def get_conn():
    # create parent folder if needed
    parent = os.path.dirname(DB_PATH)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages (
      message_id TEXT PRIMARY KEY,
      from_msisdn TEXT NOT NULL,
      to_msisdn TEXT NOT NULL,
      ts TEXT NOT NULL,
      text TEXT,
      created_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()

def db_is_ready() -> bool:
    try:
        conn = get_conn()
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception:
        return False

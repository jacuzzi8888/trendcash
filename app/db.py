import os
import sqlite3
from datetime import datetime, timezone


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vercel provides a writable /tmp directory if we absolutely need sqlite,
# but we prefer Turso. If not on Vercel, use local data folder.
is_vercel = os.environ.get("VERCEL") == "1"
if is_vercel:
    DEFAULT_DB_PATH = "/tmp/ntc.db"
else:
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "ntc.db")

# Force Turso if URL is provided
USE_TURSO = "TURSO_DATABASE_URL" in os.environ and os.environ.get("TURSO_DATABASE_URL") != ""


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_db():
    if USE_TURSO:
        from .db_turso import get_turso_db
        return get_turso_db()
    
    db_path = os.environ.get("NTC_DB_PATH", DEFAULT_DB_PATH)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    if USE_TURSO:
        from .db_turso import init_turso_db
        init_turso_db()
        return
    
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS trend_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            velocity_score REAL NOT NULL,
            advertiser_safety_score REAL NOT NULL,
            commercial_intent_score REAL NOT NULL,
            evergreen_score REAL NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_trend_candidates_created_at
            ON trend_candidates(created_at);

        CREATE TABLE IF NOT EXISTS source_packs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            publisher TEXT NOT NULL,
            published_at TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(candidate_id) REFERENCES trend_candidates(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            status TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            image_policy TEXT NOT NULL DEFAULT 'none',
            image_prompt TEXT,
            target_site_id INTEGER,
            FOREIGN KEY(candidate_id) REFERENCES trend_candidates(id) ON DELETE CASCADE,
            FOREIGN KEY(target_site_id) REFERENCES sites(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS qc_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            source_valid INTEGER NOT NULL,
            unique_value INTEGER NOT NULL,
            advertiser_safety INTEGER NOT NULL,
            actionability INTEGER NOT NULL,
            reviewer TEXT,
            reviewed_at TEXT NOT NULL,
            FOREIGN KEY(draft_id) REFERENCES drafts(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS publish_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            site_id INTEGER,
            status TEXT NOT NULL,
            post_id TEXT,
            published_url TEXT,
            published_at TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(draft_id) REFERENCES drafts(id) ON DELETE CASCADE,
            FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            category TEXT NOT NULL,
            published_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_date TEXT NOT NULL,
            indexing_rate REAL,
            queries INTEGER,
            ctr REAL,
            avg_position REAL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            niche TEXT NOT NULL,
            description TEXT,
            api_url TEXT NOT NULL,
            api_key TEXT,
            categories TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS publish_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            draft_id INTEGER NOT NULL,
            site_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            response TEXT,
            published_url TEXT,
            published_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(draft_id) REFERENCES drafts(id) ON DELETE CASCADE,
            FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE CASCADE
        );
        """
    )
    _seed_defaults(conn)
    conn.commit()
    conn.close()


def _seed_defaults(conn):
    defaults = {
        "category_locked": "",
        "publish_daily_limit": "10",
        "image_policy_default": "none",
        "source_days_back": "7",
        "sources_per_trend": "3",
        "auto_fetch_sources": "true",
    }
    for key, value in defaults.items():
        cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cur.fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)", (key, value)
            )


def get_setting(conn, key, default=None):
    cur = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    if row is None:
        return default
    return row["value"]


def set_setting(conn, key, value):
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )


def utc_now():
    return _utc_now()

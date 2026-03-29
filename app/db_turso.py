import os
import json
import requests
from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN', '')

# Convert libsql:// URL to https:// for HTTP API
def _get_http_url():
    url = TURSO_DATABASE_URL
    if url.startswith('libsql://'):
        url = 'https://' + url[9:]
    return url


def get_turso_db():
    if not TURSO_DATABASE_URL:
        raise RuntimeError("TURSO_DATABASE_URL not set")
    if not TURSO_AUTH_TOKEN:
        raise RuntimeError("TURSO_AUTH_TOKEN not set")
    return TursoConnection()


class TursoRow:
    def __init__(self, data, columns):
        self._data = dict(zip(columns, data))
    
    def __getitem__(self, key):
        return self._data[key]
    
    def keys(self):
        return self._data.keys()


class TursoCursor:
    def __init__(self, rows, columns):
        self._rows = rows or []
        self._columns = columns or []
        self.rowcount = len(self._rows)
        self.description = [(col,) for col in self._columns]
    
    def fetchone(self):
        if self._rows:
            return TursoRow(self._rows[0], self._columns)
        return None
    
    def fetchall(self):
        return [TursoRow(row, self._columns) for row in self._rows]


class TursoConnection:
    def __init__(self):
        self.url = _get_http_url()
        self.token = TURSO_AUTH_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def execute(self, sql, params=None):
        params = params or ()
        if isinstance(params, list):
            params = tuple(params)
        
        payload = {
            'statements': [
                {'q': sql, 'params': list(params)}
            ]
        }
        
        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Turso error: {response.status_code} - {response.text}")
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            stmt_result = result[0]
            if 'error' in stmt_result:
                raise RuntimeError(f"SQL error: {stmt_result['error']}")
            
            results = stmt_result.get('results', {})
            columns = results.get('columns', [])
            rows = results.get('rows', [])
            return TursoCursor(rows, columns)
        
        return TursoCursor([], [])
    
    def executescript(self, sql):
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            self.execute(stmt)
    
    def commit(self):
        pass
    
    def close(self):
        pass


def init_turso_db():
    conn = get_turso_db()
    conn.executescript("""
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
    """)
    
    defaults = {
        "category_locked": "",
        "publish_daily_limit": "10",
        "image_policy_default": "none",
    }
    for key, value in defaults.items():
        result = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        if result.fetchone() is None:
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.close()


def utc_now():
    return _utc_now()

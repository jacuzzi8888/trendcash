import os
from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN', '')


def get_turso_db():
    if not TURSO_DATABASE_URL:
        raise RuntimeError("TURSO_DATABASE_URL not set")
    
    try:
        import libsql_experimental as libsql
        conn = libsql.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
        return TursoConnection(conn)
    except ImportError:
        raise RuntimeError("libsql-experimental not installed")


class TursoRow:
    def __init__(self, data):
        self._data = data
    
    def __getitem__(self, key):
        return self._data[key]
    
    def keys(self):
        return self._data.keys()


class TursoCursor:
    def __init__(self, rows, columns):
        self._rows = rows or []
        self._columns = columns or []
        self.rowcount = len(self._rows)
    
    def fetchone(self):
        if self._rows:
            return TursoRow(dict(zip(self._columns, self._rows[0])))
        return None
    
    def fetchall(self):
        return [TursoRow(dict(zip(self._columns, row))) for row in self._rows]


class TursoConnection:
    def __init__(self, conn):
        self._conn = conn
    
    def execute(self, sql, params=None):
        params = self._normalize_params(params)
        cursor = self._conn.execute(sql, params)
        
        columns = []
        rows = []
        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
        
        return TursoCursor(rows, columns)
    
    def executescript(self, sql):
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            self.execute(stmt)
    
    def commit(self):
        pass
    
    def close(self):
        pass
    
    def _normalize_params(self, params):
        if params is None:
            return ()
        if isinstance(params, list):
            return tuple(params)
        if isinstance(params, tuple):
            return params
        return params


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
            conn.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.close()


def utc_now():
    return _utc_now()

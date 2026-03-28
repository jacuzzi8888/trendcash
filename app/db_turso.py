import os
from datetime import datetime, timezone


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


TURSO_DATABASE_URL = os.environ.get('TURSO_DATABASE_URL', '')
TURSO_AUTH_TOKEN = os.environ.get('TURSO_AUTH_TOKEN', '')

_turso_connection = None


def get_turso_connection():
    global _turso_connection
    if _turso_connection is not None:
        return _turso_connection
    
    try:
        import libsql_experimental as libsql
        raw_conn = libsql.connect(TURSO_DATABASE_URL, auth_token=TURSO_AUTH_TOKEN)
        
        class TursoResult:
            def __init__(self, cursor):
                self.columns = [description[0] for description in cursor.description] if cursor.description else []
                self.rows = cursor.fetchall()
        
        class ConnectionWrapper:
            def __init__(self, conn):
                self._conn = conn
                
            def execute(self, sql, params=None):
                if params is None:
                    params = ()
                elif isinstance(params, list):
                    params = tuple(params)
                return self._conn.execute(sql, params)
                
            def query(self, sql, params=None):
                if params is None:
                    params = ()
                elif isinstance(params, list):
                    params = tuple(params)
                cursor = self._conn.execute(sql, params)
                return TursoResult(cursor)
                
        _turso_connection = ConnectionWrapper(raw_conn)
        return _turso_connection
    except ImportError:
        raise RuntimeError("No libsql client available. Install libsql-experimental.")


def turso_execute(sql, params=None):
    conn = get_turso_connection()
    return conn.query(sql, params or [])


def turso_executescript(sql):
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    for stmt in statements:
        turso_execute(stmt)


def init_turso_db():
    turso_executescript("""
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
    _seed_defaults_turso()


def _seed_defaults_turso():
    defaults = {
        "category_locked": "",
        "publish_daily_limit": "10",
        "image_policy_default": "none",
    }
    for key, value in defaults.items():
        result = turso_execute("SELECT value FROM settings WHERE key = ?", [key])
        if not result or not result.rows or len(result.rows) == 0:
            turso_execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)", [key, value]
            )


class TursoRow:
    def __init__(self, data):
        self._data = data
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __iter__(self):
        return iter(self._data.keys())


class TursoCursor:
    def __init__(self, result):
        self._result = result
        self._rows = None
    
    @property
    def rowcount(self):
        return len(self._result.rows) if self._result and hasattr(self._result, 'rows') else 0
    
    def fetchone(self):
        if self._result and hasattr(self._result, 'rows') and self._result.rows:
            return TursoRow(dict(zip(self._result.columns, self._result.rows[0])))
        return None
    
    def fetchall(self):
        if self._result and hasattr(self._result, 'rows') and self._result.rows:
            return [TursoRow(dict(zip(self._result.columns, row))) for row in self._result.rows]
        return []


class TursoConnection:
    def __init__(self):
        self._client = get_turso_connection()
    
    def execute(self, sql, params=None):
        result = self._client.query(sql, params or [])
        return TursoCursor(result)
    
    def executescript(self, sql):
        turso_executescript(sql)
    
    def commit(self):
        pass
    
    def close(self):
        pass


def get_turso_db():
    return TursoConnection()


def utc_now():
    return _utc_now()

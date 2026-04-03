"""
Database connection pooling and management.
Provides connection pooling for both SQLite and Turso.
"""

import os
import threading
import time
from contextlib import contextmanager
from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime, timezone

import sqlite3

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

from .schema import SCHEMA_SQL, INDEX_SQL, DEFAULT_SETTINGS


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IS_VERCEL = os.environ.get("VERCEL") == "1"
USE_TURSO = bool(os.environ.get("TURSO_DATABASE_URL"))

if IS_VERCEL:
    DEFAULT_DB_PATH = "/tmp/ntc.db"
else:
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "ntc.db")


class ConnectionPool:
    """Thread-safe connection pool for SQLite."""
    
    def __init__(self, db_path: str, max_connections: int = 10, timeout: int = 30):
        self.db_path = db_path
        self.max_connections = max_connections
        self.timeout = timeout
        self._pool: List[sqlite3.Connection] = []
        self._lock = threading.Lock()
        self._created = 0
    
    def _create_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        conn.execute("PRAGMA cache_size = -64000;")
        return conn
    
    def get(self) -> sqlite3.Connection:
        with self._lock:
            if self._pool:
                return self._pool.pop()
            if self._created < self.max_connections:
                self._created += 1
                return self._create_connection()
        
        time.sleep(0.1)
        return self.get()
    
    def return_connection(self, conn: sqlite3.Connection):
        with self._lock:
            if len(self._pool) < self.max_connections:
                self._pool.append(conn)
            else:
                conn.close()
                self._created -= 1
    
    def close_all(self):
        with self._lock:
            for conn in self._pool:
                conn.close()
            self._pool.clear()
            self._created = 0


_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                db_path = os.environ.get("NTC_DB_PATH", DEFAULT_DB_PATH)
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                _pool = ConnectionPool(db_path)
    return _pool


class TursoConnection:
    """Turso HTTP API connection with connection reuse."""
    
    __slots__ = ['url', '_session', '_closed']
    
    def __init__(self):
        self.url = self._get_http_url()
        self._session = self._get_session()
        self._closed = False
    
    @staticmethod
    def _get_http_url() -> str:
        url = os.environ.get('TURSO_DATABASE_URL', '')
        if url.startswith('libsql://'):
            url = 'https://' + url[9:]
        return url
    
    _session_instance = None
    
    @classmethod
    def _get_session(cls):
        if cls._session_instance is None:
            if not REQUESTS_AVAILABLE:
                raise RuntimeError("requests library required for Turso")
            cls._session_instance = requests.Session()
            cls._session_instance.headers.update({
                'Authorization': f'Bearer {os.environ.get("TURSO_AUTH_TOKEN", "")}',
                'Content-Type': 'application/json'
            })
        return cls._session_instance
    
    def execute(self, sql: str, params: tuple = None) -> 'TursoCursor':
        if self._closed:
            raise RuntimeError("Connection is closed")
        
        params = params or ()
        if isinstance(params, list):
            params = tuple(params)
        
        payload = {
            'statements': [
                {'q': sql, 'params': list(params)}
            ]
        }
        
        response = self._session.post(
            self.url,
            json=payload,
            timeout=15
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
            
            lastrowid = None
            if sql.strip().upper().startswith('INSERT'):
                try:
                    id_result = self._session.post(
                        self.url,
                        json={'statements': [{'q': 'SELECT last_insert_rowid() as id'}]},
                        timeout=10
                    )
                    if id_result.status_code == 200:
                        id_data = id_result.json()
                        if id_data and len(id_data) > 0:
                            id_rows = id_data[0].get('results', {}).get('rows', [])
                            if id_rows:
                                lastrowid = id_rows[0][0]
                except Exception:
                    pass
            
            return TursoCursor(rows, columns, lastrowid)
        
        return TursoCursor([], [])
    
    def executescript(self, sql: str):
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        for stmt in statements:
            self.execute(stmt)
    
    def commit(self):
        pass
    
    def close(self):
        self._closed = True
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class TursoRow:
    __slots__ = ['_data']
    
    def __init__(self, data: list, columns: list):
        self._data = dict(zip(columns, data))
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)
    
    def keys(self) -> list:
        return list(self._data.keys())
    
    def __repr__(self):
        return f"TursoRow({self._data})"


class TursoCursor:
    __slots__ = ['_rows', '_columns', 'rowcount', 'description', 'lastrowid']
    
    def __init__(self, rows: list, columns: list, lastrowid: int = None):
        self._rows = rows or []
        self._columns = columns or []
        self.rowcount = len(self._rows)
        self.description = [(col,) for col in self._columns]
        self.lastrowid = lastrowid
    
    def fetchone(self) -> Optional[TursoRow]:
        if self._rows:
            return TursoRow(self._rows[0], self._columns)
        return None
    
    def fetchall(self) -> List[TursoRow]:
        return [TursoRow(row, self._columns) for row in self._rows]


class DatabaseConnection:
    """Unified database connection wrapper."""
    
    def __init__(self):
        self._conn = None
        self._is_turso = USE_TURSO
    
    def __enter__(self):
        if self._is_turso:
            self._conn = TursoConnection()
        else:
            self._conn = get_pool().get()
        return self._conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._conn:
            if exc_type:
                try:
                    self._conn.rollback()
                except:
                    pass
            self._conn.close()
            self._conn = None


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = None
    try:
        if USE_TURSO:
            conn = TursoConnection()
        else:
            conn = get_pool().get()
        yield conn
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


def init_db():
    """Initialize database with schema and indexes."""
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.executescript(INDEX_SQL)
        
        for key, value in DEFAULT_SETTINGS.items():
            result = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
            if result.fetchone() is None:
                conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
        
        conn.commit()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_setting(conn, key: str, default: str = None) -> Optional[str]:
    from .cache import SettingsCache
    
    cached = SettingsCache.get(key)
    if cached is not None:
        return cached
    
    result = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = result.fetchone()
    if row:
        SettingsCache.set(key, row["value"])
        return row["value"]
    return default


def set_setting(conn, key: str, value: str):
    from .cache import SettingsCache
    
    conn.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    SettingsCache.set(key, value)


def execute_batch(conn, sql: str, params_list: List[tuple]) -> int:
    """Execute multiple inserts/updates efficiently."""
    count = 0
    for params in params_list:
        conn.execute(sql, params)
        count += 1
    return count


def paginate_query(conn, base_sql: str, params: tuple, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Execute paginated query."""
    offset = (page - 1) * per_page
    
    count_sql = f"SELECT COUNT(*) as total FROM ({base_sql}) as subq"
    count_result = conn.execute(count_sql, params).fetchone()
    total = count_result["total"] if count_result else 0
    
    data_sql = f"{base_sql} LIMIT ? OFFSET ?"
    data_params = params + (per_page, offset)
    rows = conn.execute(data_sql, data_params).fetchall()
    
    return {
        "items": rows,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page,
    }

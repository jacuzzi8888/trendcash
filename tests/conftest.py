import os
import sys
import pytest
import tempfile
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db import get_db, init_db


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    
    test_config = {
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'LOGIN_DISABLED': True,
    }
    
    os.environ['NTC_DB_PATH'] = db_path
    os.environ['NTC_SECRET_KEY'] = 'test-secret-key-minimum-32-characters-long'
    
    app = create_app(test_config=test_config)
    
    with app.app_context():
        init_db()
        with get_db() as conn:
            from app.auth import init_default_user
            init_default_user(conn)
    
    yield app
    
    # Close any open connections before cleanup
    try:
        conn = sqlite3.connect(db_path)
        conn.close()
    except:
        pass
    
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass  # File still locked, that's okay for tests


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def db(app):
    with app.app_context():
        # Get a direct sqlite connection for tests to avoid context manager issues in tests
        db_path = os.environ.get('NTC_DB_PATH')
        conn = sqlite3.connect(db_path, timeout=5)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Initialize schema for test
        from app.schema import SCHEMA_SQL, INDEX_SQL
        conn.executescript(SCHEMA_SQL)
        conn.executescript(INDEX_SQL)
        conn.commit()
        
        yield conn
        conn.close()


class AuthActions:
    def __init__(self, client):
        self._client = client


@pytest.fixture
def auth(client):
    return AuthActions(client)

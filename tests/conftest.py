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
    }
    
    os.environ['NTC_DB_PATH'] = db_path
    os.environ.pop('TURSO_DATABASE_URL', None)
    
    app = create_app()
    app.config.update(test_config)
    
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
        conn = get_db()
        yield conn
        try:
            conn.close()
        except:
            pass


class AuthActions:
    def __init__(self, client):
        self._client = client


@pytest.fixture
def auth(client):
    return AuthActions(client)

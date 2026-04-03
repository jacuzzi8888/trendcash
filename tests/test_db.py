import pytest
from app.db import get_db, get_setting, set_setting, utc_now


def test_get_db_returns_connection(app):
    with app.app_context():
        with get_db() as conn:
            assert conn is not None
            assert hasattr(conn, 'execute')


def test_init_db_creates_tables(app):
    with app.app_context():
        with get_db() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t['name'] for t in tables]
            
            assert 'trend_candidates' in table_names
            assert 'source_packs' in table_names
            assert 'drafts' in table_names
            assert 'qc_reviews' in table_names
            assert 'publish_queue' in table_names
            assert 'sites' in table_names
            assert 'settings' in table_names
            assert 'metrics' in table_names


def test_get_setting_default(db):
    value = get_setting(db, 'nonexistent_key', 'default_value')
    assert value == 'default_value'


def test_set_and_get_setting(db):
    set_setting(db, 'test_key', 'test_value')
    db.commit()
    
    value = get_setting(db, 'test_key')
    assert value == 'test_value'


def test_set_setting_updates_existing(db):
    set_setting(db, 'test_key', 'original')
    db.commit()
    
    set_setting(db, 'test_key', 'updated')
    db.commit()
    
    value = get_setting(db, 'test_key')
    assert value == 'updated'


def test_utc_now_returns_iso_format():
    result = utc_now()
    assert isinstance(result, str)
    assert 'T' in result


def test_insert_trend_candidate(db):
    db.execute(
        """INSERT INTO trend_candidates 
           (topic, category, source, velocity_score, advertiser_safety_score, 
            commercial_intent_score, evergreen_score, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ('Test Topic', 'Test Category', 'Test Source', 0.5, 0.5, 0.5, 0.5, utc_now())
    )
    db.commit()
    
    result = db.execute(
        "SELECT * FROM trend_candidates WHERE topic = ?", ('Test Topic',)
    ).fetchone()
    
    assert result is not None
    assert result['topic'] == 'Test Topic'
    assert result['category'] == 'Test Category'


def test_insert_draft(db):
    db.execute(
        """INSERT INTO trend_candidates 
           (topic, category, source, velocity_score, advertiser_safety_score, 
            commercial_intent_score, evergreen_score, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ('Draft Topic', 'News', 'Google Trends', 1.0, 1.0, 1.0, 1.0, utc_now())
    )
    candidate_id = db.execute(
        "SELECT id FROM trend_candidates WHERE topic = ?", ('Draft Topic',)
    ).fetchone()['id']
    
    now = utc_now()
    db.execute(
        """INSERT INTO drafts 
           (candidate_id, title, content, status, last_updated, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (candidate_id, 'Test Title', 'Test Content', 'draft', now, now, now)
    )
    db.commit()
    
    result = db.execute(
        "SELECT * FROM drafts WHERE title = ?", ('Test Title',)
    ).fetchone()
    
    assert result is not None
    assert result['status'] == 'draft'


def test_insert_site(db):
    now = utc_now()
    db.execute(
        """INSERT INTO sites 
           (name, slug, niche, api_url, api_key, is_active, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ('Test Site', 'test-site', 'News', 'https://example.com/api', 'key123', 1, now, now)
    )
    db.commit()
    
    result = db.execute(
        "SELECT * FROM sites WHERE slug = ?", ('test-site',)
    ).fetchone()
    
    assert result is not None
    assert result['name'] == 'Test Site'
    assert result['is_active'] == 1

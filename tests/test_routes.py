import pytest
from app.db import utc_now


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Naija Trend-to-Cash' in response.data


def test_settings_get(client):
    response = client.get('/settings')
    assert response.status_code == 200
    assert b'Publish daily limit' in response.data


def test_settings_post(client):
    response = client.post('/settings', data={
        'publish_daily_limit': '15',
        'image_policy_default': 'priority'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_trends_get(client):
    response = client.get('/trends')
    assert response.status_code == 200


def test_trends_post_add_candidate(client):
    response = client.post('/trends', data={
        'topic': 'Test Trend Topic',
        'category': 'Technology',
        'source': 'Google Trends',
        'velocity_score': '0.8',
        'advertiser_safety_score': '0.9',
        'commercial_intent_score': '0.7',
        'evergreen_score': '0.6'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Trend Topic' in response.data


def test_drafts_get(client):
    response = client.get('/drafts')
    assert response.status_code == 200


def test_qc_get(client):
    response = client.get('/qc')
    assert response.status_code == 200


def test_publish_get(client):
    response = client.get('/publish')
    assert response.status_code == 200


def test_metrics_get(client):
    response = client.get('/metrics')
    assert response.status_code == 200


def test_sites_get(client):
    response = client.get('/sites/')
    assert response.status_code == 200


def test_selection_get(client):
    response = client.get('/selection')
    assert response.status_code == 200


def test_discover_get(client):
    response = client.get('/discover')
    assert response.status_code == 200


def test_404_error(client):
    response = client.get('/nonexistent-page')
    assert response.status_code == 404


def test_create_draft_requires_sources(client, db):
    db.execute(
        """INSERT INTO trend_candidates 
           (topic, category, source, velocity_score, advertiser_safety_score, 
            commercial_intent_score, evergreen_score, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        ('No Sources Topic', 'News', 'Test', 0.5, 0.5, 0.5, 0.5, utc_now())
    )
    db.commit()
    
    result = db.execute(
        "SELECT id FROM trend_candidates WHERE topic = ?", ('No Sources Topic',)
    ).fetchone()
    candidate_id = result['id']
    
    response = client.post(f'/drafts/new/{candidate_id}', follow_redirects=True)
    assert b'At least 2 sources required' in response.data


def test_full_workflow(client, db):
    candidate_response = client.post('/trends', data={
        'topic': 'Workflow Test Topic',
        'category': 'Finance',
        'source': 'Test Source',
        'velocity_score': '0.9',
        'advertiser_safety_score': '0.9',
        'commercial_intent_score': '0.9',
        'evergreen_score': '0.9'
    }, follow_redirects=True)
    assert candidate_response.status_code == 200
    
    result = db.execute(
        "SELECT id FROM trend_candidates WHERE topic = ?", ('Workflow Test Topic',)
    ).fetchone()
    candidate_id = result['id']
    
    for i in range(2):
        client.post(f'/sources/{candidate_id}', data={
            'url': f'https://example.com/article{i}',
            'publisher': f'Publisher {i}',
            'published_at': '2024-01-01',
            'notes': f'Test source {i}'
        }, follow_redirects=True)
    
    sources = db.execute(
        "SELECT COUNT(*) as count FROM source_packs WHERE candidate_id = ?",
        (candidate_id,)
    ).fetchone()
    assert sources['count'] == 2

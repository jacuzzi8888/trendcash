import json
import requests
from .db import get_db, utc_now


def publish_to_site(site_id, draft):
    conn = get_db()
    site = conn.execute(
        "SELECT * FROM sites WHERE id = ? AND is_active = 1", (site_id,)
    ).fetchone()
    
    if site is None:
        conn.close()
        return {"success": False, "error": "Site not found or inactive"}
    
    candidate = conn.execute(
        "SELECT t.category FROM trend_candidates t "
        "JOIN drafts d ON d.candidate_id = t.id "
        "WHERE d.id = ?",
        (draft["id"],),
    ).fetchone()
    conn.close()
    
    category = candidate["category"] if candidate else "general"
    excerpt = draft["content"].split("\n", 1)[0].replace("#", "").strip()[:200]
    slug = _slugify(draft["title"])
    
    payload = {
        "title": draft["title"],
        "content": draft["content"],
        "category": category,
        "tags": [],
        "slug": slug,
        "meta": {
            "excerpt": excerpt,
            "image_url": None
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {site['api_key']}"
    }
    
    try:
        response = requests.post(
            site["api_url"],
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "post_id": data.get("post_id"),
                "published_url": data.get("url"),
                "response": json.dumps(data)
            }
        else:
            return {
                "success": False,
                "error": f"API returned {response.status_code}: {response.text}"
            }
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def log_publish(draft_id, site_id, result):
    conn = get_db()
    status = "success" if result.get("success") else "failed"
    conn.execute(
        """
        INSERT INTO publish_log
        (draft_id, site_id, status, response, published_url, published_at, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            draft_id,
            site_id,
            status,
            result.get("response") or result.get("error"),
            result.get("published_url"),
            utc_now() if status == "success" else None,
            utc_now()
        )
    )
    conn.commit()
    conn.close()


def get_publish_history(draft_id=None, site_id=None, limit=50):
    conn = get_db()
    query = """
        SELECT pl.*, s.name as site_name, d.title as draft_title
        FROM publish_log pl
        JOIN sites s ON pl.site_id = s.id
        JOIN drafts d ON pl.draft_id = d.id
    """
    params = []
    conditions = []
    
    if draft_id:
        conditions.append("pl.draft_id = ?")
        params.append(draft_id)
    if site_id:
        conditions.append("pl.site_id = ?")
        params.append(site_id)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY pl.created_at DESC LIMIT ?"
    params.append(limit)
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def _slugify(value):
    cleaned = []
    last_dash = False
    for ch in value.lower():
        if ch.isalnum():
            cleaned.append(ch)
            last_dash = False
        else:
            if not last_dash:
                cleaned.append("-")
                last_dash = True
    slug = "".join(cleaned).strip("-")
    return slug or "post"

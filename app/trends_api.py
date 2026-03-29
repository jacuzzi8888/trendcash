import requests
import json
from datetime import datetime, timezone

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

SEED_KEYWORDS_NIGERIA = [
    'nigeria', 'naira', 'fuel price', 'cbn', 'jamb', 'asuu', 'inec',
    'bitcoin', 'dollar', 'exchange rate', 'immigration', 'recruitment',
    'bank loan', 'scholarship', 'visa', 'passport', 'election',
    'football', 'super eagles', 'premier league',
    'davido', 'burna boy', 'wizkid', 'tinubu', 'lagos'
]


def get_autocomplete_topics(keyword):
    url = f'https://trends.google.com/trends/api/autocomplete/{keyword}'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            text = r.text
            if text.startswith(')]}'):
                text = text[5:]
            data = json.loads(text)
            return data.get('default', {}).get('topics', [])
    except Exception:
        pass
    return []


def fetch_all_trends(geo='NG'):
    all_trends = []
    seen = set()
    
    for keyword in SEED_KEYWORDS_NIGERIA:
        topics = get_autocomplete_topics(keyword)
        for t in topics:
            title = t.get('title', '')
            if title and title.lower() not in seen:
                seen.add(title.lower())
                all_trends.append({
                    'topic': title,
                    'source': 'google_autocomplete',
                    'geo': geo,
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                })
    
    return {
        'success': True,
        'trends': all_trends,
        'count': len(all_trends),
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }


def get_suggestions(keyword):
    topics = get_autocomplete_topics(keyword)
    results = []
    for t in topics:
        results.append({
            'title': t.get('title', ''),
            'type': t.get('type', '')
        })
    return {'success': True, 'suggestions': results}


def get_interest_over_time(keywords, geo='NG', timeframe='now 7-d'):
    return {'success': True, 'data': []}


def get_related_topics(keyword, geo='NG'):
    return {'success': True, 'rising': [], 'top': []}


def get_related_queries(keyword, geo='NG'):
    topics = get_autocomplete_topics(keyword)
    queries = []
    for t in topics:
        queries.append({
            'query': t.get('title', ''),
            'value': 0
        })
    return {'success': True, 'rising': queries[:5], 'top': queries[:10]}

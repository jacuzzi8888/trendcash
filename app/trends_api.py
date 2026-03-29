import requests
import json
from datetime import datetime, timezone

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

SEED_KEYWORDS_NIGERIA = [
    'nigeria news', 'nigerian', 'nigeria election', 'nigeria football',
    'naira to dollar', 'naira exchange', 'nigerian naira',
    'cbn nigeria', 'central bank nigeria',
    'jamb 2026', 'jamb result', 'jamb portal',
    'asuu strike', 'asuu news',
    'inec nigeria', 'inec voter',
    'nigerian immigration', 'nigeria passport',
    'nigeria visa', 'travel to nigeria',
    'davido nigeria', 'burna boy', 'wizkid nigeria',
    'super eagles', 'nigeria premier league',
    'fuel scarcity nigeria', 'fuel price nigeria',
    'lagos nigeria', 'abuja nigeria',
    'nigeria banking', 'nigeria loan',
    'bitcoin nigeria', 'crypto nigeria',
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
    
    nigeria_terms = [
        'nigeria', 'nigerian', 'naira', 'lagos', 'abuja', 'ibadan',
        'kano', 'port harcourt', 'benin', 'kaduna', 'jos',
        'super eagles', 'falcons', 'npfl', 'npl',
        'jamb', 'waec', 'neco', 'asuu', 'nysc',
        'inec', 'pvc', 'apc', 'pdp', 'labour party',
        'cbn', 'gtbank', 'access bank', 'uba', 'zenith',
        'dangote', 'nnpc', 'mtn nigeria',
        'davido', 'burna boy', 'wizkid', 'tiwa savage', 'rema',
        'afrobeat', 'afrobeats', 'nollywood',
        'fuel', 'petrol', 'diesel', 'kerosene',
        'visa', 'passport', 'immigration',
        'scholarship', 'recruitment', 'job',
    ]
    
    for keyword in SEED_KEYWORDS_NIGERIA:
        topics = get_autocomplete_topics(keyword)
        for t in topics:
            title = t.get('title', '')
            title_lower = title.lower()
            if title and title_lower not in seen:
                is_relevant = any(term in title_lower for term in nigeria_terms)
                if is_relevant or len(title) > 10:
                    seen.add(title_lower)
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

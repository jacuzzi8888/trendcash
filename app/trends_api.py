import requests
import json
from datetime import datetime, timezone

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

CATEGORY_KEYWORDS = {
    'betting': [
        'betting nigeria', 'sports betting nigeria', 'bet9ja', '1xbet nigeria',
        'sportybet', 'nairabet', 'betking nigeria', 'betway nigeria',
        'betting tips nigeria', 'football betting nigeria', 'virtual betting',
        'bookmaker nigeria', 'betting sites nigeria', 'bet bonus nigeria',
    ],
    'crypto': [
        'bitcoin nigeria', 'crypto nigeria', 'binance nigeria',
        'usdt nigeria', 'ethereum nigeria', 'crypto exchange nigeria',
        'p2p crypto nigeria', 'buy bitcoin nigeria', 'sell bitcoin nigeria',
        'crypto wallet nigeria', 'crypto trading nigeria',
    ],
    'finance': [
        'loan nigeria', 'loan app nigeria', 'quick loan nigeria',
        'bank loan nigeria', 'personal loan nigeria', 'business loan nigeria',
        'carbon loan', 'fairmoney', 'branch loan', 'palmcredit',
        'naira to dollar', 'exchange rate nigeria', 'cbn exchange rate',
        'forex nigeria', 'dollar to naira today',
    ],
    'education': [
        'jamb 2026', 'jamb result', 'jamb portal', 'waec result',
        'neco result', 'nysc registration', 'nysc portal',
        'asuu strike', 'asuu news', 'university admission nigeria',
        'scholarship nigeria', 'post utme', 'jamb caps',
    ],
    'politics': [
        'inec nigeria', 'pvc registration', 'nigeria election',
        'nigeria news', 'tinubu', 'nigeria government',
        'nigeria senate', 'house of representatives nigeria',
    ],
    'sports': [
        'super eagles', 'nigeria football', 'npfl', 'nigerian premier league',
        'afcon', 'world cup qualifier nigeria', 'nfl nigeria',
        'premier league', 'champions league', 'la liga',
    ],
    'entertainment': [
        'davido', 'burna boy', 'wizkid', 'tiwa savage', 'rema',
        'nollywood', 'nigerian movies', 'afrobeats', 'nigerian music',
        'bbnaija', 'big brother naija',
    ],
    'travel': [
        'nigeria passport', 'immigration nigeria', 'visa nigeria',
        'travel to nigeria', 'nigeria visa free countries',
        'lagos airport', 'abuja airport', 'flight nigeria',
    ],
    'jobs': [
        'nigeria recruitment', 'job vacancy nigeria', 'federal government jobs',
        'nigeria immigration recruitment', 'nigeria police recruitment',
        'nscdc recruitment', 'n-power', 'nysc jobs',
    ],
    'general': [
        'nigeria news', 'nigerian', 'nigeria today', 'lagos nigeria',
        'abuja nigeria', 'fuel price nigeria', 'nigeria economy',
    ],
}

NIGERIA_TERMS = [
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
    'bet', 'betting', 'sporty', '9ja', 'king', 'naira',
    'bitcoin', 'crypto', 'binance', 'usdt',
    'loan', 'bank', 'credit',
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


def fetch_all_trends(geo='NG', category='general'):
    all_trends = []
    seen = set()
    
    category_lower = category.lower().strip() if category else 'general'
    
    if category_lower in CATEGORY_KEYWORDS:
        keywords = CATEGORY_KEYWORDS[category_lower]
    else:
        keywords = [
            f'{category_lower} nigeria',
            f'{category_lower} lagos',
            f'{category_lower} abuja',
            f'nigeria {category_lower}',
            f'{category_lower} news nigeria',
            f'{category_lower} africa',
            f'best {category_lower} nigeria',
            f'{category_lower} jobs nigeria',
        ]
    
    for keyword in keywords:
        topics = get_autocomplete_topics(keyword)
        for t in topics:
            title = t.get('title', '')
            title_lower = title.lower()
            if title and title_lower not in seen:
                is_relevant = any(term in title_lower for term in NIGERIA_TERMS)
                if is_relevant or len(title) > 10:
                    seen.add(title_lower)
                    all_trends.append({
                        'topic': title,
                        'source': 'google_autocomplete',
                        'geo': geo,
                        'category_hint': category_lower,
                        'fetched_at': datetime.now(timezone.utc).isoformat()
                    })
    
    return {
        'success': True,
        'trends': all_trends,
        'count': len(all_trends),
        'category': category_lower,
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

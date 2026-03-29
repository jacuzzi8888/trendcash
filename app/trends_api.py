import time
from datetime import datetime, timezone
from pytrends.request import TrendReq


FALLBACK_TRENDS = [
    {"topic": "Naira to Dollar exchange rate today", "category": "Finance"},
    {"topic": "Fuel price increase Nigeria 2026", "category": "Economy"},
    {"topic": "CBN new policy on forex", "category": "Finance"},
    {"topic": "ASUU strike latest news", "category": "Education"},
    {"topic": "JAMB result 2026 checking portal", "category": "Education"},
    {"topic": "Nigeria vs Ghana match", "category": "Sports"},
    {"topic": "Super Eagles World Cup qualifiers", "category": "Sports"},
    {"topic": "INEC voter registration deadline", "category": "Politics"},
    {"topic": "Nigerian passport application process", "category": "Travel"},
    {"topic": "Bitcoin price in Naira", "category": "Finance"},
    {"topic": "Lagos traffic situation today", "category": "Transport"},
    {"topic": "Burna Boy new album 2026", "category": "Entertainment"},
    {"topic": "Davido latest song release", "category": "Entertainment"},
    {"topic": "Wizkid concert in Lagos", "category": "Entertainment"},
    {"topic": "Nigeria inflation rate 2026", "category": "Economy"},
    {"topic": "Bank loan interest rates Nigeria", "category": "Finance"},
    {"topic": "Scholarship opportunities for Nigerians", "category": "Education"},
    {"topic": "Nigeria immigration recruitment", "category": "Jobs"},
    {"topic": "Premier League fixtures this weekend", "category": "Sports"},
    {"topic": "Champions League final 2026", "category": "Sports"},
    {"topic": "Abuja real estate prices", "category": "Real Estate"},
    {"topic": "Nigeria visa free countries 2026", "category": "Travel"},
    {"topic": "Tinubu government latest news", "category": "Politics"},
    {"topic": "NNPC fuel scarcity update", "category": "Economy"},
    {"topic": "Nigeria electricity tariff increase", "category": "Utilities"},
]

POPULAR_NIGERIA_KEYWORDS = [
    "naira", "fuel price", "cbn", "asuu", "jamb", "inec", "nigeria",
    "bitcoin", "dollar", "exchange rate", "immigration", "recruitment",
    "bank", "loan", "scholarship", "visa", "passport", "election",
    "football", "afcon", "super eagles", "premier league", "champions league",
    "davido", "burna boy", "wizkid", "buhari", "tinubu", "lagos", "abuja"
]


def get_pytrends_client():
    return TrendReq(hl='en-US', tz=360)


def get_trending_keywords(geo='NG'):
    pytrends = get_pytrends_client()
    results = []
    
    try:
        trending = pytrends.trending_searches()
        if trending is not None and not trending.empty:
            for idx, row in trending.iterrows():
                results.append({
                    'topic': row[0] if len(row) > 0 else str(row),
                    'source': 'google_trends_trending',
                    'geo': geo,
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                })
    except Exception:
        pass
    
    return results


def get_suggested_trends(keywords=None, geo='NG'):
    pytrends = get_pytrends_client()
    results = []
    seen = set()
    
    search_keywords = keywords or POPULAR_NIGERIA_KEYWORDS[:3]
    
    for kw in search_keywords[:3]:
        try:
            suggestions = pytrends.suggestions(kw)
            for s in suggestions[:5]:
                title = s.get('title', '')
                if title and title.lower() not in seen:
                    seen.add(title.lower())
                    results.append({
                        'topic': title,
                        'source': 'google_suggestions',
                        'geo': geo,
                        'fetched_at': datetime.now(timezone.utc).isoformat()
                    })
        except Exception:
            continue
    
    return results


def get_related_trends(keyword, geo='NG'):
    pytrends = get_pytrends_client()
    results = []
    seen = set()
    
    try:
        pytrends.build_payload([keyword], geo=geo.upper() if geo else 'NG', timeframe='now 7-d')
        queries = pytrends.related_queries()
        
        if keyword in queries:
            if queries[keyword].get('top') is not None:
                for idx, row in queries[keyword]['top'].iterrows():
                    query = row.get('query', '')
                    if query and query.lower() not in seen:
                        seen.add(query.lower())
                        results.append({
                            'topic': query,
                            'source': 'google_related_queries',
                            'geo': geo,
                            'fetched_at': datetime.now(timezone.utc).isoformat()
                        })
    except Exception:
        pass
    
    return results


def get_interest_over_time(keywords, geo='NG', timeframe='now 7-d'):
    pytrends = get_pytrends_client()
    try:
        pytrends.build_payload(keywords, geo=geo.upper() if geo else 'NG', timeframe=timeframe)
        data = pytrends.interest_over_time()
        if data is None or data.empty:
            return {'success': True, 'data': []}
        results = []
        for idx, row in data.iterrows():
            point = {'date': idx.isoformat()}
            for kw in keywords:
                point[kw] = int(row[kw]) if kw in row else 0
            results.append(point)
        return {'success': True, 'data': results}
    except Exception as e:
        return {'success': False, 'error': str(e), 'data': []}


def get_related_topics(keyword, geo='NG'):
    pytrends = get_pytrends_client()
    try:
        pytrends.build_payload([keyword], geo=geo.upper() if geo else 'NG', timeframe='now 7-d')
        topics = pytrends.related_topics()
        results = {'rising': [], 'top': []}
        if keyword in topics:
            if topics[keyword].get('rising') is not None:
                for idx, row in topics[keyword]['rising'].iterrows():
                    results['rising'].append({
                        'topic': row.get('topic_title', ''),
                        'type': row.get('topic_type', ''),
                        'value': row.get('value', 0)
                    })
            if topics[keyword].get('top') is not None:
                for idx, row in topics[keyword]['top'].iterrows():
                    results['top'].append({
                        'topic': row.get('topic_title', ''),
                        'type': row.get('topic_type', ''),
                        'value': row.get('value', 0)
                    })
        return {'success': True, **results}
    except Exception as e:
        return {'success': False, 'error': str(e), 'rising': [], 'top': []}


def get_related_queries(keyword, geo='NG'):
    pytrends = get_pytrends_client()
    try:
        pytrends.build_payload([keyword], geo=geo.upper() if geo else 'NG', timeframe='now 7-d')
        queries = pytrends.related_queries()
        results = {'rising': [], 'top': []}
        if keyword in queries:
            if queries[keyword].get('rising') is not None:
                for idx, row in queries[keyword]['rising'].iterrows():
                    results['rising'].append({
                        'query': row.get('query', ''),
                        'value': row.get('value', 0)
                    })
            if queries[keyword].get('top') is not None:
                for idx, row in queries[keyword]['top'].iterrows():
                    results['top'].append({
                        'query': row.get('query', ''),
                        'value': row.get('value', 0)
                    })
        return {'success': True, **results}
    except Exception as e:
        return {'success': False, 'error': str(e), 'rising': [], 'top': []}


def get_suggestions(keyword):
    pytrends = get_pytrends_client()
    try:
        suggestions = pytrends.suggestions(keyword)
        results = []
        for s in suggestions:
            results.append({
                'title': s.get('title', ''),
                'type': s.get('type', '')
            })
        return {'success': True, 'suggestions': results}
    except Exception as e:
        return {'success': False, 'error': str(e), 'suggestions': []}


def fetch_all_trends(geo='NG'):
    all_trends = []
    seen = set()
    
    try:
        trending = get_trending_keywords(geo)
        for t in trending:
            topic_lower = t['topic'].lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                all_trends.append(t)
    except Exception:
        pass
    
    try:
        suggested = get_suggested_trends(keywords=['nigeria', 'naira', 'fuel'], geo=geo)
        for t in suggested:
            topic_lower = t['topic'].lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                all_trends.append(t)
    except Exception:
        pass
    
    try:
        for kw in ['nigeria', 'naira']:
            related = get_related_trends(kw, geo)
            for t in related:
                topic_lower = t['topic'].lower()
                if topic_lower not in seen:
                    seen.add(topic_lower)
                    all_trends.append(t)
    except Exception:
        pass
    
    if len(all_trends) < 10:
        for trend in FALLBACK_TRENDS:
            topic_lower = trend['topic'].lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                all_trends.append({
                    'topic': trend['topic'],
                    'source': 'curated_fallback',
                    'geo': geo,
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                })
    
    return {
        'success': True,
        'trends': all_trends,
        'count': len(all_trends),
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }

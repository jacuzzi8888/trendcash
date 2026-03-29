import time
from datetime import datetime, timezone
from pytrends.request import TrendReq


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
    
    search_keywords = keywords or POPULAR_NIGERIA_KEYWORDS
    
    for kw in search_keywords[:10]:
        try:
            suggestions = pytrends.suggestions(kw)
            for s in suggestions[:3]:
                title = s.get('title', '')
                if title and title.lower() not in seen:
                    seen.add(title.lower())
                    results.append({
                        'topic': title,
                        'source': 'google_suggestions',
                        'geo': geo,
                        'fetched_at': datetime.now(timezone.utc).isoformat()
                    })
            time.sleep(0.5)
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
        time.sleep(0.5)
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
    
    trending = get_trending_keywords(geo)
    for t in trending:
        topic_lower = t['topic'].lower()
        if topic_lower not in seen:
            seen.add(topic_lower)
            all_trends.append(t)
    
    suggested = get_suggested_trends(geo=geo)
    for t in suggested:
        topic_lower = t['topic'].lower()
        if topic_lower not in seen:
            seen.add(topic_lower)
            all_trends.append(t)
    
    seed_keywords = ['nigeria', 'naira', 'fuel', 'cbn', 'jamb', 'asuu', 'inec']
    for kw in seed_keywords:
        related = get_related_trends(kw, geo)
        for t in related:
            topic_lower = t['topic'].lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                all_trends.append(t)
        time.sleep(0.5)
    
    return {
        'success': True,
        'trends': all_trends,
        'count': len(all_trends),
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }

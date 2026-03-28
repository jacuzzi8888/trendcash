import time
from datetime import datetime, timezone
from pytrends.request import TrendReq


def get_pytrends_client():
    return TrendReq(hl='en-US', tz=360)


def get_daily_trends(geo='NG'):
    pytrends = get_pytrends_client()
    try:
        trending_searches = pytrends.trending_searches(pn=geo.lower() if geo else 'nigeria')
        results = []
        for idx, row in trending_searches.iterrows():
            results.append({
                'topic': row[0] if len(row) > 0 else str(row),
                'source': 'google_trends_daily',
                'geo': geo,
                'fetched_at': datetime.now(timezone.utc).isoformat()
            })
        return {'success': True, 'trends': results}
    except Exception as e:
        return {'success': False, 'error': str(e), 'trends': []}


def get_realtime_trends(geo='NG'):
    pytrends = get_pytrends_client()
    try:
        realtime = pytrends.trending_searches_realtime(pn=geo.upper() if geo else 'NG')
        results = []
        if realtime is not None and not realtime.empty:
            for idx, row in realtime.iterrows():
                topic = row.get('title', str(row))
                results.append({
                    'topic': topic,
                    'source': 'google_trends_realtime',
                    'geo': geo,
                    'fetched_at': datetime.now(timezone.utc).isoformat()
                })
        return {'success': True, 'trends': results}
    except Exception as e:
        return {'success': False, 'error': str(e), 'trends': []}


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
            if topics[keyword]['rising'] is not None:
                for idx, row in topics[keyword]['rising'].iterrows():
                    results['rising'].append({
                        'topic': row.get('topic_title', ''),
                        'type': row.get('topic_type', ''),
                        'value': row.get('value', 0)
                    })
            if topics[keyword]['top'] is not None:
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
            if queries[keyword]['rising'] is not None:
                for idx, row in queries[keyword]['rising'].iterrows():
                    results['rising'].append({
                        'query': row.get('query', ''),
                        'value': row.get('value', 0)
                    })
            if queries[keyword]['top'] is not None:
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
    daily = get_daily_trends(geo)
    realtime = get_realtime_trends(geo)
    all_trends = []
    seen = set()
    if daily['success']:
        for t in daily['trends']:
            topic_lower = t['topic'].lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                all_trends.append(t)
    if realtime['success']:
        for t in realtime['trends']:
            topic_lower = t['topic'].lower()
            if topic_lower not in seen:
                seen.add(topic_lower)
                all_trends.append(t)
    return {
        'success': True,
        'trends': all_trends,
        'count': len(all_trends),
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }

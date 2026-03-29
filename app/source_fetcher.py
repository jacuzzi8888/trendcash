import os
import requests
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional


SERPER_API_KEY = os.environ.get('SERPER_API_KEY', '')
SERPER_API_URL = 'https://google.serper.dev/search'


def fetch_sources(
    topic: str,
    num_results: int = 3,
    days_back: int = 7,
    region: str = 'NG'
) -> Dict:
    """
    Fetch news sources for a topic using Serper.dev API.
    
    Args:
        topic: The trend topic to search for
        num_results: Number of sources to return (1-10)
        days_back: Only include articles from last N days
        region: Country code for regional results
    
    Returns:
        Dict with 'success', 'sources', and optional 'error'
    """
    if not SERPER_API_KEY:
        return {
            'success': False,
            'error': 'SERPER_API_KEY not configured',
            'sources': []
        }
    
    search_query = f"{topic} Nigeria news"
    
    payload = {
        'q': search_query,
        'num': min(num_results, 10),
        'gl': region.lower() if region else 'ng',
        'hl': 'en',
        'tbs': _get_date_filter(days_back) if days_back > 0 else None,
    }
    
    payload = {k: v for k, v in payload.items() if v is not None}
    
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            SERPER_API_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 401:
            return {
                'success': False,
                'error': 'Invalid Serper API key',
                'sources': []
            }
        
        if response.status_code == 429:
            return {
                'success': False,
                'error': 'Serper API quota exceeded',
                'sources': []
            }
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Serper API error: {response.status_code}',
                'sources': []
            }
        
        data = response.json()
        sources = _parse_serper_results(data, days_back)
        
        return {
            'success': True,
            'sources': sources[:num_results],
            'query': search_query,
            'total_found': len(sources)
        }
        
    except requests.Timeout:
        return {
            'success': False,
            'error': 'Serper API timeout',
            'sources': []
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'sources': []
        }


def _get_date_filter(days_back: int) -> str:
    """Generate Google date filter string for Serper API."""
    if days_back <= 0:
        return ''
    return f'qdr:d{days_back}'


def _parse_serper_results(data: Dict, days_back: int) -> List[Dict]:
    """Parse Serper API response into source list."""
    sources = []
    
    # Try 'news' results first (better for news articles)
    news_results = data.get('news', [])
    organic_results = data.get('organic', [])
    
    results = news_results if news_results else organic_results
    
    cutoff_date = None
    if days_back > 0:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    for item in results:
        source = _extract_source_info(item, cutoff_date)
        if source:
            sources.append(source)
    
    return sources


def _extract_source_info(item: Dict, cutoff_date: Optional[datetime]) -> Optional[Dict]:
    """Extract source info from a Serper result item."""
    url = item.get('link') or item.get('url')
    title = item.get('title', '')
    
    if not url or not title:
        return None
    
    publisher = item.get('source') or item.get('displayLink', '')
    if publisher.startswith('www.'):
        publisher = publisher[4:]
    
    published_at = _parse_date(item.get('date') or item.get('snippetHighlighted', ''))
    
    if cutoff_date and published_at:
        try:
            pub_dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            if pub_dt < cutoff_date:
                return None
        except:
            pass
    
    snippet = item.get('snippet', '')
    
    return {
        'url': url,
        'publisher': publisher,
        'title': title,
        'published_at': published_at,
        'notes': snippet[:200] if snippet else title,
        'fetched_at': datetime.now(timezone.utc).isoformat()
    }


def _parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats from Serper results."""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Try ISO format
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        pass
    
    # Try common formats
    formats = [
        '%Y-%m-%d',
        '%d %b %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%B %d, %Y',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except:
            pass
    
    # Relative dates
    date_str_lower = date_str.lower()
    now = datetime.now(timezone.utc)
    
    if 'hour' in date_str_lower or 'minute' in date_str_lower:
        return now.strftime('%Y-%m-%d')
    if 'yesterday' in date_str_lower:
        return (now - timedelta(days=1)).strftime('%Y-%m-%d')
    if 'day' in date_str_lower:
        try:
            days = int(''.join(filter(str.isdigit, date_str_lower)) or '1')
            return (now - timedelta(days=days)).strftime('%Y-%m-%d')
        except:
            pass
    if 'week' in date_str_lower:
        try:
            weeks = int(''.join(filter(str.isdigit, date_str_lower)) or '1')
            return (now - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        except:
            pass
    
    return None


def fetch_sources_for_trends(
    trends: List[Dict],
    sources_per_trend: int = 3,
    days_back: int = 7,
    region: str = 'NG'
) -> Dict[int, List[Dict]]:
    """
    Fetch sources for multiple trends.
    
    Returns:
        Dict mapping trend index to list of sources
    """
    results = {}
    
    for i, trend in enumerate(trends):
        topic = trend.get('topic', '')
        if not topic:
            continue
        
        result = fetch_sources(
            topic=topic,
            num_results=sources_per_trend,
            days_back=days_back,
            region=region
        )
        
        if result['success']:
            results[i] = result['sources']
        else:
            results[i] = []
    
    return results

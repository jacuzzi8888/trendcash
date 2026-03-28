import argparse
import json
import sys
from datetime import datetime, timezone

sys.path.insert(0, '.')

from app.db import get_db, init_db, utc_now
from app.trends_api import fetch_all_trends, get_daily_trends, get_realtime_trends


def store_trend(conn, topic, source, category='general', scores=None):
    if scores is None:
        scores = {
            'velocity': 0.5,
            'advertiser_safety': 0.5,
            'commercial_intent': 0.5,
            'evergreen': 0.5
        }
    
    existing = conn.execute(
        "SELECT id FROM trend_candidates WHERE topic = ? AND source LIKE ?",
        (topic, 'google_trends%')
    ).fetchone()
    
    if existing:
        return False, existing['id']
    
    conn.execute(
        """
        INSERT INTO trend_candidates
        (topic, category, source, velocity_score, advertiser_safety_score,
         commercial_intent_score, evergreen_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            topic,
            category,
            source,
            scores['velocity'],
            scores['advertiser_safety'],
            scores['commercial_intent'],
            scores['evergreen'],
            utc_now()
        )
    )
    return True, None


def fetch_and_store(geo='NG', category='general', default_scores=None):
    init_db()
    conn = get_db()
    
    result = fetch_all_trends(geo)
    
    if not result['success']:
        print(f"Error fetching trends: {result.get('error', 'Unknown error')}")
        conn.close()
        return {'success': False, 'error': result.get('error')}
    
    added = 0
    skipped = 0
    
    for trend in result['trends']:
        topic = trend['topic']
        source = trend['source']
        
        inserted, _ = store_trend(conn, topic, source, category, default_scores)
        if inserted:
            added += 1
        else:
            skipped += 1
    
    conn.commit()
    conn.close()
    
    print(f"Fetched {result['count']} trends")
    print(f"Added: {added}, Skipped (duplicates): {skipped}")
    
    return {
        'success': True,
        'fetched': result['count'],
        'added': added,
        'skipped': skipped
    }


def main():
    parser = argparse.ArgumentParser(description='Fetch trends from Google Trends')
    parser.add_argument('--geo', default='NG', help='Geographic region (default: NG for Nigeria)')
    parser.add_argument('--category', default='general', help='Category to assign to fetched trends')
    parser.add_argument('--velocity', type=float, default=0.5, help='Default velocity score')
    parser.add_argument('--advertiser-safety', type=float, default=0.5, help='Default advertiser safety score')
    parser.add_argument('--commercial-intent', type=float, default=0.5, help='Default commercial intent score')
    parser.add_argument('--evergreen', type=float, default=0.5, help='Default evergreen score')
    parser.add_argument('--output', help='Output JSON file path (optional)')
    
    args = parser.parse_args()
    
    scores = {
        'velocity': args.velocity,
        'advertiser_safety': args.advertiser_safety,
        'commercial_intent': args.commercial_intent,
        'evergreen': args.evergreen
    }
    
    result = fetch_and_store(geo=args.geo, category=args.category, default_scores=scores)
    
    if args.output and result['success']:
        output_data = {
            'fetched_at': datetime.now(timezone.utc).isoformat(),
            'geo': args.geo,
            'category': args.category,
            'result': result
        }
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Output saved to {args.output}")


if __name__ == '__main__':
    main()

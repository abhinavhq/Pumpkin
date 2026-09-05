"""
Test script for search analytics
"""

import time
import logging
from app.analytics.analytics import SearchAnalytics

logging.basicConfig(level=logging.INFO)


def test_analytics():
    print("\n" + "="*50)
    print("📊 TESTING SEARCH ANALYTICS")
    print("="*50 + "\n")
    
    analytics = SearchAnalytics()
    
    test_queries = [
        ("python programming", 3, 12.5),
        ("web development", 2, 8.3),
        ("data science", 4, 15.2),
        ("python programming", 5, 10.1),
        ("search engine", 0, 5.2),
        ("machine learning", 3, 11.8),
        ("artificial intelligence", 2, 9.7),
        ("web development", 3, 7.5),
        ("data science", 4, 14.9),
        ("unknown topic", 0, 4.3),
    ]
    
    print("📝 Tracking searches...")
    for query, results, latency in test_queries:
        analytics.track_search(query, results, latency)
        print(f"   ✅ '{query}' → {results} results, {latency}ms")
        time.sleep(0.1)
    
    stats = analytics.get_stats()
    print(f"\n📊 Statistics:")
    print(f"   Total Searches: {stats['total_searches']}")
    print(f"   Zero-Result Searches: {stats['zero_result_searches']}")
    print(f"   Zero-Result Rate: {stats['zero_result_rate']}%")
    print(f"   Average Latency: {stats['avg_latency']}ms")
    print(f"   Unique Queries: {stats['unique_queries']}")
    
    print(f"\n📈 Top Queries:")
    for i, q in enumerate(stats['top_queries'], 1):
        print(f"   {i}. '{q['query']}' ({q['count']} searches)")
    
    print(f"\n🕐 Recent Searches:")
    recent = analytics.get_recent_searches(5)
    for s in recent:
        print(f"   - '{s['query']}' ({s['results_count']} results, {s['latency_ms']}ms)")
    
    print(f"\n❌ Zero-Result Queries:")
    zero_queries = analytics.get_zero_result_queries()
    for q in zero_queries:
        print(f"   - '{q['query']}' ({q['count']} times)")
    
    print("\n" + "="*50)
    print("✅ Analytics test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_analytics()

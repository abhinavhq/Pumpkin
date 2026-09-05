"""
Analytics - Track and analyze search behavior
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict, Counter
from pathlib import Path

logger = logging.getLogger(__name__)


class SearchAnalytics:
    """
    Track search analytics and generate insights
    """
    
    def __init__(self, storage_path: str = "data/analytics.json"):
        self.storage_path = storage_path
        self.data = self._load_data()
        logger.info("SearchAnalytics initialized")
    
    def _load_data(self) -> Dict:
        """Load analytics data from file"""
        if Path(self.storage_path).exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                return self._init_data()
        return self._init_data()
    
    def _init_data(self) -> Dict:
        """Initialize empty analytics data"""
        return {
            'searches': [],
            'total_searches': 0,
            'zero_result_searches': 0,
            'total_latency': 0.0,
            'queries': {},
            'daily_stats': {},
            'hourly_stats': {}
        }
    
    def _save_data(self):
        """Save analytics data to file"""
        Path(self.storage_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def track_search(
        self,
        query: str,
        results_count: int,
        latency_ms: float,
        mode: str = "web"
    ):
        """
        Track a search event
        """
        now = datetime.now()
        timestamp = now.isoformat()
        
        # Store search record
        search_record = {
            'query': query,
            'results_count': results_count,
            'latency_ms': latency_ms,
            'mode': mode,
            'timestamp': timestamp
        }
        
        self.data['searches'].append(search_record)
        self.data['total_searches'] += 1
        
        # Track zero-result searches
        if results_count == 0:
            self.data['zero_result_searches'] += 1
        
        # Track latency
        self.data['total_latency'] += latency_ms
        
        # Track query frequency
        self.data['queries'][query] = self.data['queries'].get(query, 0) + 1
        
        # Track daily stats
        date_key = now.strftime("%Y-%m-%d")
        if date_key not in self.data['daily_stats']:
            self.data['daily_stats'][date_key] = {'searches': 0, 'zero_results': 0}
        self.data['daily_stats'][date_key]['searches'] += 1
        if results_count == 0:
            self.data['daily_stats'][date_key]['zero_results'] += 1
        
        # Track hourly stats
        hour_key = now.strftime("%Y-%m-%d %H:00")
        if hour_key not in self.data['hourly_stats']:
            self.data['hourly_stats'][hour_key] = {'searches': 0, 'zero_results': 0}
        self.data['hourly_stats'][hour_key]['searches'] += 1
        if results_count == 0:
            self.data['hourly_stats'][hour_key]['zero_results'] += 1
        
        # Save after each search (can be optimized to batch)
        self._save_data()
        
        logger.debug(f"Tracked search: '{query}' ({results_count} results, {latency_ms:.2f}ms)")
    
    def get_stats(self) -> Dict:
        """Get overall analytics statistics"""
        total = self.data['total_searches']
        zero_results = self.data['zero_result_searches']
        
        return {
            'total_searches': total,
            'zero_result_searches': zero_results,
            'zero_result_rate': round(zero_results / total * 100, 2) if total > 0 else 0,
            'avg_latency': round(self.data['total_latency'] / total, 2) if total > 0 else 0,
            'unique_queries': len(self.data['queries']),
            'top_queries': self.get_top_queries(10)
        }
    
    def get_top_queries(self, limit: int = 10) -> List[Dict]:
        """Get most popular queries"""
        queries = self.data['queries']
        sorted_queries = sorted(queries.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'query': q, 'count': c}
            for q, c in sorted_queries[:limit]
        ]
    
    def get_daily_stats(self, days: int = 7) -> List[Dict]:
        """Get daily statistics for the last N days"""
        result = []
        now = datetime.now()
        
        for i in range(days):
            date = now - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            
            stats = self.data['daily_stats'].get(date_key, {'searches': 0, 'zero_results': 0})
            result.append({
                'date': date_key,
                'searches': stats['searches'],
                'zero_results': stats['zero_results']
            })
        
        return result
    
    def get_hourly_stats(self, hours: int = 24) -> List[Dict]:
        """Get hourly statistics for the last N hours"""
        result = []
        now = datetime.now()
        
        for i in range(hours):
            hour = now - timedelta(hours=i)
            hour_key = hour.strftime("%Y-%m-%d %H:00")
            
            stats = self.data['hourly_stats'].get(hour_key, {'searches': 0, 'zero_results': 0})
            result.append({
                'hour': hour_key,
                'searches': stats['searches'],
                'zero_results': stats['zero_results']
            })
        
        return result
    
    def get_recent_searches(self, limit: int = 20) -> List[Dict]:
        """Get most recent searches"""
        searches = self.data['searches'][-limit:]
        return searches[::-1]  # Reverse to show newest first
    
    def get_zero_result_queries(self) -> List[Dict]:
        """Get queries that returned zero results"""
        zero_result_searches = [
            s for s in self.data['searches']
            if s['results_count'] == 0
        ]
        
        # Count zero-result queries
        query_counts = Counter([s['query'] for s in zero_result_searches])
        
        return [
            {'query': q, 'count': c}
            for q, c in query_counts.most_common(20)
        ]
    
    def clear_old_data(self, days: int = 30):
        """Clear data older than N days"""
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()
        
        # Filter searches
        self.data['searches'] = [
            s for s in self.data['searches']
            if s['timestamp'] > cutoff_str
        ]
        
        # Recalculate stats
        self._recalculate_stats()
        self._save_data()
        logger.info(f"Cleared data older than {days} days")
    
    def _recalculate_stats(self):
        """Recalculate statistics from search records"""
        searches = self.data['searches']
        
        total = len(searches)
        zero_results = sum(1 for s in searches if s['results_count'] == 0)
        total_latency = sum(s['latency_ms'] for s in searches)
        
        self.data['total_searches'] = total
        self.data['zero_result_searches'] = zero_results
        self.data['total_latency'] = total_latency
        
        # Recalculate query frequencies
        query_counts = Counter([s['query'] for s in searches])
        self.data['queries'] = dict(query_counts)
        
        # Recalculate daily stats
        daily_stats = defaultdict(lambda: {'searches': 0, 'zero_results': 0})
        for s in searches:
            date_key = s['timestamp'][:10]  # YYYY-MM-DD
            daily_stats[date_key]['searches'] += 1
            if s['results_count'] == 0:
                daily_stats[date_key]['zero_results'] += 1
        self.data['daily_stats'] = dict(daily_stats)
        
        # Recalculate hourly stats
        hourly_stats = defaultdict(lambda: {'searches': 0, 'zero_results': 0})
        for s in searches:
            hour_key = s['timestamp'][:13] + ":00"  # YYYY-MM-DD HH:00
            hourly_stats[hour_key]['searches'] += 1
            if s['results_count'] == 0:
                hourly_stats[hour_key]['zero_results'] += 1
        self.data['hourly_stats'] = dict(hourly_stats)
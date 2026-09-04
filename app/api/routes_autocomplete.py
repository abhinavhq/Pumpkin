"""
Autocomplete API - Search suggestions as users type
"""

import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, Query, HTTPException

from app.query.processor import QueryProcessor

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store for popular queries
popular_queries = []
query_frequency = {}


class AutocompleteEngine:
    """Engine for providing search suggestions"""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        
        # Seed with some popular queries
        self._seed_queries()
    
    def _seed_queries(self):
        """Seed with initial popular queries"""
        seed_queries = [
            "python programming",
            "python for beginners",
            "python data science",
            "python web development",
            "python machine learning",
            "python tutorial",
            "python flask",
            "python django",
            "python pandas",
            "python numpy",
            "javascript tutorial",
            "reactjs guide",
            "web development",
            "data science",
            "machine learning",
            "artificial intelligence"
        ]
        
        for query in seed_queries:
            self.add_query(query)
    
    def add_query(self, query: str):
        """Add a query to the popularity tracking"""
        query_lower = query.lower().strip()
        if query_lower:
            query_frequency[query_lower] = query_frequency.get(query_lower, 0) + 1
            self._update_popular_queries()
    
    def get_suggestions(
        self,
        prefix: str,
        limit: int = 10,
        typo_tolerance: bool = True
    ) -> List[Dict]:
        """
        Get autocomplete suggestions for a prefix
        """
        if not prefix or len(prefix) < 1:
            return []
        
        prefix_lower = prefix.lower().strip()
        
        # 1. Find matching queries
        matches = []
        
        for query, freq in query_frequency.items():
            # Check if query starts with prefix
            if query.startswith(prefix_lower):
                matches.append((query, freq))
            
            # Check typo tolerance
            elif typo_tolerance and self._is_typo(query, prefix_lower):
                matches.append((query, freq // 2))  # Lower priority for typos
        
        # 2. Sort by frequency (popularity)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        # 3. Format results
        suggestions = []
        for query, freq in matches[:limit]:
            suggestions.append({
                'text': query,
                'frequency': freq,
                'type': 'query'
            })
        
        return suggestions
    
    def _is_typo(self, query: str, prefix: str) -> bool:
        """Check if prefix is a typo of query"""
        # Simple check: if prefix is close to the start of query
        if len(prefix) < 3:
            return False
        
        # Check if query contains prefix with one character difference
        for i in range(len(query) - len(prefix) + 1):
            substr = query[i:i+len(prefix)]
            diff = sum(1 for a, b in zip(substr, prefix) if a != b)
            if diff <= 1:
                return True
        
        return False
    
    def _update_popular_queries(self):
        """Update the popular queries list"""
        global popular_queries
        popular_queries = sorted(
            query_frequency.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]


# Initialize autocomplete engine
autocomplete_engine = AutocompleteEngine()


# --- Endpoints ---

@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1, description="Prefix to autocomplete"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions")
):
    """
    Get autocomplete suggestions for a prefix
    """
    suggestions = autocomplete_engine.get_suggestions(q, limit=limit)
    
    return {
        'prefix': q,
        'suggestions': suggestions,
        'total': len(suggestions)
    }


@router.post("/autocomplete/track")
async def track_query(
    query: str = Query(..., description="Query to track for popularity")
):
    """
    Track a query for popularity (called when user searches)
    """
    autocomplete_engine.add_query(query)
    return {'status': 'tracked', 'query': query}


@router.get("/autocomplete/popular")
async def get_popular_queries(
    limit: int = Query(10, ge=1, le=50, description="Number of popular queries")
):
    """
    Get the most popular queries
    """
    popular = query_frequency.items()
    sorted_popular = sorted(popular, key=lambda x: x[1], reverse=True)[:limit]
    
    return {
        'popular_queries': [
            {'query': q, 'frequency': f} for q, f in sorted_popular
        ]
    }
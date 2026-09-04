"""
Related Searches API - Find related queries
"""

import logging
from typing import List, Dict, Set
from fastapi import APIRouter, Query

from app.query.processor import QueryProcessor

logger = logging.getLogger(__name__)

router = APIRouter()

# Query history for generating related searches
query_history = {}
query_graph = {}


class RelatedSearchesEngine:
    """Engine for generating related searches"""
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self._seed_related_queries()
    
    def _seed_related_queries(self):
        """Seed with initial related query data"""
        self.add_related_cluster("python", [
            "python programming",
            "python for beginners",
            "python data science",
            "python web development",
            "python machine learning",
            "python tutorial",
            "python django",
            "python flask"
        ])
        
        self.add_related_cluster("web", [
            "web development",
            "web design",
            "web applications",
            "web security"
        ])
        
        self.add_related_cluster("data", [
            "data science",
            "data analytics",
            "data visualization",
            "data engineering"
        ])
    
    def add_related_cluster(self, keyword: str, queries: List[str]):
        """Add a cluster of related queries"""
        keyword_lower = keyword.lower()
        
        if keyword_lower not in query_graph:
            query_graph[keyword_lower] = set()
        
        for query in queries:
            query_lower = query.lower()
            query_graph[keyword_lower].add(query_lower)
            
            if query_lower not in query_history:
                query_history[query_lower] = 1
            else:
                query_history[query_lower] += 1
    
    def get_related(self, query: str, limit: int = 8) -> List[str]:
        """Get related searches for a query"""
        if not query:
            return []
        
        query_lower = query.lower().strip()
        related = set()
        tokens = self.query_processor._tokenize(query_lower)
        
        for token in tokens:
            if token in query_graph:
                related.update(query_graph[token])
        
        related.discard(query_lower)
        
        filtered = []
        for rel in related:
            rel_tokens = set(self.query_processor._tokenize(rel))
            if rel_tokens & set(tokens):
                filtered.append(rel)
        
        filtered.sort(key=lambda x: query_history.get(x, 0), reverse=True)
        return filtered[:limit]


related_engine = RelatedSearchesEngine()


@router.get("/related")
async def get_related_searches(
    q: str = Query(..., min_length=1, description="Query to find related searches for"),
    limit: int = Query(8, ge=1, le=20, description="Number of related searches")
):
    """Get related searches for a query"""
    related = related_engine.get_related(q, limit=limit)
    return {
        'query': q,
        'related_searches': related,
        'total': len(related)
    }
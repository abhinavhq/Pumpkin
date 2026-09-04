"""
Advanced Ranker - Combines multiple ranking signals
"""

import logging
import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class AdvancedRanker:
    """
    Advanced ranking with multiple signals:
    - BM25 score
    - Title match
    - Heading match
    - Document freshness
    - Domain authority (simulated)
    """
    
    def __init__(
        self,
        weight_bm25: float = 0.30,
        weight_title: float = 0.25,
        weight_heading: float = 0.20,
        weight_freshness: float = 0.15,
        weight_domain: float = 0.10,
        freshness_decay_days: int = 365
    ):
        self.weights = {
            'bm25': weight_bm25,
            'title': weight_title,
            'heading': weight_heading,
            'freshness': weight_freshness,
            'domain': weight_domain
        }
        self.freshness_decay_days = freshness_decay_days
        self.domain_authority = self._init_domain_authority()
        logger.info(f"Initialized AdvancedRanker with weights: {self.weights}")
    
    def rank(
        self,
        query: str,
        query_tokens: List[str],
        documents: List[Dict]
    ) -> List[Tuple[str, float, Dict]]:
        scored_docs = []
        
        for doc in documents:
            doc_id = doc.get('id', '')
            title = doc.get('title', '')
            content = doc.get('content', '')
            headings = doc.get('headings', {})
            created_at = doc.get('created_at')
            url = doc.get('url', '')
            bm25_score = doc.get('bm25_score', 0.0)
            
            signals = {}
            signals['bm25'] = bm25_score
            signals['title'] = self._title_match_score(title, query_tokens)
            signals['heading'] = self._heading_match_score(headings, query_tokens)
            signals['freshness'] = self._freshness_score(created_at)
            signals['domain'] = self._domain_score(url)
            
            final_score = self._combine_scores(signals)
            scored_docs.append((doc_id, final_score, signals))
        
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs
    
    def _title_match_score(self, title: str, query_tokens: List[str]) -> float:
        if not title or not query_tokens:
            return 0.0
        
        title_lower = title.lower()
        matched_terms = sum(1 for token in query_tokens if token in title_lower)
        ratio = matched_terms / len(query_tokens)
        query_lower = ' '.join(query_tokens).lower()
        exact_match = 1.0 if query_lower in title_lower else 0.0
        return min(1.0, ratio * 0.8 + exact_match * 0.2)
    
    def _heading_match_score(self, headings: Dict, query_tokens: List[str]) -> float:
        if not headings or not query_tokens:
            return 0.0
        
        heading_weights = {'h1': 1.0, 'h2': 0.8, 'h3': 0.6, 'h4': 0.4, 'h5': 0.3, 'h6': 0.2}
        total_score = 0.0
        total_weight = 0.0
        
        for heading_level, heading_list in headings.items():
            if not heading_list:
                continue
            weight = heading_weights.get(heading_level, 0.3)
            for heading in heading_list:
                heading_lower = heading.lower()
                matched_terms = sum(1 for token in query_tokens if token in heading_lower)
                if matched_terms > 0:
                    ratio = matched_terms / len(query_tokens)
                    total_score += ratio * weight
                    total_weight += weight
        
        if total_weight == 0:
            return 0.0
        return min(1.0, total_score / total_weight)
    
    def _freshness_score(self, created_at: Optional[datetime]) -> float:
        if not created_at:
            return 0.5
        try:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now()
            days_old = (now - created_at).days
            score = math.exp(-days_old / self.freshness_decay_days)
            return max(0.0, min(1.0, score))
        except Exception:
            return 0.5
    
    def _domain_score(self, url: str) -> float:
        if not url:
            return 0.3
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
        except:
            return 0.3
        return self.domain_authority.get(domain, 0.3)
    
    def _combine_scores(self, signals: Dict[str, float]) -> float:
        final_score = 0.0
        for signal, weight in self.weights.items():
            score = signals.get(signal, 0.0)
            final_score += score * weight
        return min(1.0, max(0.0, final_score))
    
    def _init_domain_authority(self) -> Dict[str, float]:
        return {
            'wikipedia.org': 1.0,
            'github.com': 0.9,
            'stackoverflow.com': 0.9,
            'python.org': 0.85,
            'docs.python.org': 0.85,
            'medium.com': 0.7,
            'dev.to': 0.7,
            'realpython.com': 0.75,
            'example.com': 0.5,
            'test.com': 0.5,
        }

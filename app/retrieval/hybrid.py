"""
Hybrid Search - Combines BM25 and Semantic Search
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

from app.indexing.bm25 import BM25
from app.retrieval.semantic import SemanticSearch

logger = logging.getLogger(__name__)


class HybridSearch:
    """
    Hybrid search combining BM25 and Semantic Search
    
    final_score = (weight_bm25 × bm25_score) + (weight_semantic × semantic_score)
    """
    
    def __init__(
        self,
        weight_bm25: float = 0.5,
        weight_semantic: float = 0.5,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize hybrid search
        
        Args:
            weight_bm25: Weight for BM25 scores (0-1)
            weight_semantic: Weight for semantic scores (0-1)
            model_name: Model name for semantic search
        """
        self.weight_bm25 = weight_bm25
        self.weight_semantic = weight_semantic
        
        self.bm25 = BM25()
        self.semantic = SemanticSearch(model_name)
        
        self.documents: Dict[str, Dict] = {}
        
        logger.info(f"Initialized Hybrid Search with weights: BM25={weight_bm25}, Semantic={weight_semantic}")
    
    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """
        Add a document to both search indices
        """
        # Add to BM25
        self.bm25.add_document(doc_id, title, content)
        
        # Add to semantic search
        self.semantic.add_document(doc_id, title, content)
        
        # Store document info
        self.documents[doc_id] = {
            'id': doc_id,
            'title': title,
            'content': content
        }
        
        logger.debug(f"Added document {doc_id} to hybrid index")
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Search using hybrid approach
        """
        if not self.documents:
            return []
        
        # Get BM25 results
        bm25_results = self.bm25.search(query)
        
        # Get semantic results
        semantic_results = self.semantic.search(query)
        
        # Combine scores
        combined_scores = defaultdict(float)
        
        # Process BM25 results
        if bm25_results:
            # Get max score for normalization
            max_bm25 = max([score for _, score in bm25_results]) if bm25_results else 1.0
            
            for doc_id, score in bm25_results:
                normalized_score = score / max_bm25 if max_bm25 > 0 else 0
                combined_scores[doc_id] += normalized_score * self.weight_bm25
        
        # Process semantic results
        if semantic_results:
            # Get max score for normalization
            max_semantic = max([score for _, score in semantic_results]) if semantic_results else 1.0
            
            for doc_id, score in semantic_results:
                normalized_score = score / max_semantic if max_semantic > 0 else 0
                combined_scores[doc_id] += normalized_score * self.weight_semantic
        
        # Sort by score descending
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        return sorted_results[:limit]
    
    def get_top_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Get top documents with metadata
        """
        results = self.search(query, limit)
        
        top_docs = []
        for doc_id, score in results:
            doc_info = self.documents.get(doc_id, {})
            top_docs.append({
                'id': doc_id,
                'title': doc_info.get('title', ''),
                'score': round(score, 4)
            })
        
        return top_docs
    
    def get_stats(self) -> Dict:
        """Get hybrid search statistics"""
        return {
            'total_documents': len(self.documents),
            'weight_bm25': self.weight_bm25,
            'weight_semantic': self.weight_semantic,
            'bm25_stats': self.bm25.get_stats(),
            'semantic_stats': self.semantic.get_stats()
        }

"""
Semantic Search - Vector-based similarity search
"""

import logging
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

from app.embeddings.encoder import TextEncoder

logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Semantic search using vector embeddings and cosine similarity
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.encoder = TextEncoder(model_name)
        self.documents: Dict[str, Dict] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
    
    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """
        Add a document to the semantic search index
        """
        # Combine title and content for embedding
        text = f"{title} {content}"
        embedding = self.encoder.encode(text)
        
        self.documents[doc_id] = {
            'id': doc_id,
            'title': title,
            'content': content
        }
        self.embeddings[doc_id] = embedding
        
        logger.debug(f"Added document {doc_id} (dimension: {len(embedding)})")
    
    def search(self, query: str, limit: int = 10) -> List[Tuple[str, float]]:
        """
        Search for documents similar to the query
        """
        if not self.documents:
            return []
        
        # Encode the query
        query_embedding = self.encoder.encode(query)
        
        # Calculate similarity scores
        scores = []
        for doc_id, doc_embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            scores.append((doc_id, similarity))
        
        # Sort by similarity (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores[:limit]
    
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
                'similarity': round(score, 4)
            })
        
        return top_docs
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two vectors
        """
        if vec1 is None or vec2 is None:
            return 0.0
        
        # Check if vectors are empty
        if vec1.size == 0 or vec2.size == 0:
            return 0.0
        
        # Normalize vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        dot_product = np.dot(vec1, vec2)
        return dot_product / (norm1 * norm2)
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            'total_documents': len(self.documents),
            'embedding_dimension': self.encoder.get_dimension(),
            'documents': list(self.documents.keys())
        }

"""
BM25 - Best Matching 25 ranking algorithm
"""

import math
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter

from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class BM25:
    """
    BM25 ranking algorithm for document scoring
    
    Formula:
    Score(D, Q) = Σ IDF(q) × (f(q,D) × (k1 + 1)) / (f(q,D) + k1 × (1 - b + b × |D|/avgdl))
    
    Where:
    - f(q,D) = term frequency in document
    - |D| = document length
    - avgdl = average document length
    - k1 = saturation parameter (1.2-2.0)
    - b = length normalization (0.75)
    """
    
    def __init__(
        self,
        tokenizer: Optional[Tokenizer] = None,
        k1: float = 1.2,
        b: float = 0.75
    ):
        self.tokenizer = tokenizer or Tokenizer()
        self.k1 = k1
        self.b = b
        
        self.documents: Dict[str, Dict] = {}
        self.term_document_freq: Dict[str, int] = defaultdict(int)
        self.total_documents = 0
        self.avgdl = 0.0
        self.total_terms = 0
    
    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """Add a document to the BM25 collection"""
        # Tokenize the document
        tokens = self.tokenizer.tokenize_document(title, content)
        
        if not tokens:
            logger.warning(f"No tokens found for document: {doc_id}")
            return
        
        # Count term frequencies
        term_freq = Counter(tokens)
        
        # Store document info
        self.documents[doc_id] = {
            'title': title,
            'content': content,
            'terms': tokens,
            'term_freq': dict(term_freq),
            'total_terms': len(tokens),
            'unique_terms': len(term_freq)
        }
        
        # Update document frequency for each term
        for term in set(tokens):
            self.term_document_freq[term] += 1
        
        self.total_documents += 1
        self.total_terms += len(tokens)
        self.avgdl = self.total_terms / self.total_documents if self.total_documents > 0 else 0
        
        logger.debug(f"Added document {doc_id}: {len(tokens)} terms, {len(term_freq)} unique")
    
    def get_idf(self, term: str) -> float:
        """Calculate IDF for a term"""
        df = self.term_document_freq.get(term, 0)
        
        if df == 0:
            return 0.0
        
        return math.log((self.total_documents - df + 0.5) / (df + 0.5) + 1.0)
    
    def get_term_frequency(self, doc_id: str, term: str) -> int:
        """Get term frequency in a document"""
        doc = self.documents.get(doc_id)
        if not doc:
            return 0
        return doc['term_freq'].get(term, 0)
    
    def get_document_length(self, doc_id: str) -> int:
        """Get document length"""
        doc = self.documents.get(doc_id)
        if not doc:
            return 0
        return doc['total_terms']
    
    def score_document(self, doc_id: str, query_terms: List[str]) -> float:
        """Calculate BM25 score for a document"""
        if not query_terms:
            return 0.0
        
        doc = self.documents.get(doc_id)
        if not doc:
            return 0.0
        
        doc_length = doc['total_terms']
        score = 0.0
        
        for term in query_terms:
            # Term frequency in document
            tf = doc['term_freq'].get(term, 0)
            
            if tf == 0:
                continue
            
            # IDF for the term
            idf = self.get_idf(term)
            
            if idf == 0:
                continue
            
            # BM25 term score
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avgdl))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str) -> List[Tuple[str, float]]:
        """Search for documents matching a query"""
        # Tokenize the query
        query_tokens = self.tokenizer.tokenize(query)
        
        if not query_tokens:
            return []
        
        # Score each document
        scores = []
        for doc_id in self.documents:
            score = self.score_document(doc_id, query_tokens)
            if score > 0:
                scores.append((doc_id, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    
    def get_top_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Get top documents for a query with metadata"""
        results = self.search(query)
        
        top_docs = []
        for doc_id, score in results[:limit]:
            doc_info = self.documents.get(doc_id, {})
            top_docs.append({
                'id': doc_id,
                'title': doc_info.get('title', ''),
                'score': round(score, 4),
                'total_terms': doc_info.get('total_terms', 0),
                'unique_terms': doc_info.get('unique_terms', 0)
            })
        
        return top_docs
    
    def get_document_info(self, doc_id: str) -> Optional[Dict]:
        """Get information about a document"""
        return self.documents.get(doc_id)
    
    def get_term_info(self, term: str) -> Dict:
        """Get information about a term"""
        df = self.term_document_freq.get(term, 0)
        idf = self.get_idf(term)
        
        return {
            'term': term,
            'document_frequency': df,
            'idf': round(idf, 4),
            'appears_in': [doc_id for doc_id, doc in self.documents.items() 
                          if term in doc['term_freq']]
        }
    
    def get_stats(self) -> Dict:
        """Get BM25 statistics"""
        return {
            'total_documents': self.total_documents,
            'total_terms': self.total_terms,
            'avgdl': round(self.avgdl, 2),
            'unique_terms': len(self.term_document_freq),
            'params': {
                'k1': self.k1,
                'b': self.b
            }
        }
    
    def explain_score(self, doc_id: str, query: str) -> Dict:
        """Explain how a document scored for a query"""
        query_tokens = self.tokenizer.tokenize(query)
        
        if not query_tokens:
            return {'error': 'No query tokens'}
        
        doc = self.documents.get(doc_id)
        if not doc:
            return {'error': 'Document not found'}
        
        breakdown = []
        total_score = 0.0
        doc_length = doc['total_terms']
        
        for term in query_tokens:
            tf = doc['term_freq'].get(term, 0)
            
            if tf == 0:
                continue
            
            idf = self.get_idf(term)
            
            if idf == 0:
                continue
            
            # BM25 term score
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avgdl))
            term_score = idf * (numerator / denominator)
            
            if term_score > 0:
                breakdown.append({
                    'term': term,
                    'tf': tf,
                    'idf': round(idf, 4),
                    'term_score': round(term_score, 4),
                    'contribution': round(term_score, 4)
                })
                total_score += term_score
        
        return {
            'doc_id': doc_id,
            'title': doc['title'],
            'doc_length': doc_length,
            'avgdl': round(self.avgdl, 2),
            'total_score': round(total_score, 4),
            'breakdown': breakdown,
            'query_terms': query_tokens,
            'params': {
                'k1': self.k1,
                'b': self.b
            }
        }
"""
TF-IDF - Term Frequency - Inverse Document Frequency scoring
"""

import math
import logging
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter

from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class TFIDF:
    """
    TF-IDF calculator for document scoring
    
    TF(t, d) = f(t, d) / total_terms(d)
    IDF(t) = log(N / df(t))
    TF-IDF = TF * IDF
    """
    
    def __init__(self, tokenizer: Optional[Tokenizer] = None):
        self.tokenizer = tokenizer or Tokenizer()
        self.documents: Dict[str, Dict] = {}
        self.term_document_freq: Dict[str, int] = defaultdict(int)
        self.total_documents = 0
    
    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """Add a document to the TF-IDF collection"""
        # Tokenize the document
        tokens = self.tokenizer.tokenize_document(title, content)
        
        if not tokens:
            logger.warning(f"No tokens found for document: {doc_id}")
            return
        
        # Count term frequencies in this document
        term_freq = Counter(tokens)
        
        # Store document info
        self.documents[doc_id] = {
            'title': title,
            'content': content,
            'terms': tokens,
            'term_freq': dict(term_freq),
            'total_terms': len(tokens)
        }
        
        # Update document frequency for each term
        for term in set(tokens):
            self.term_document_freq[term] += 1
        
        self.total_documents += 1
        logger.debug(f"Added document {doc_id}: {len(tokens)} terms, {len(term_freq)} unique")
    
    def get_tf(self, doc_id: str, term: str) -> float:
        """Calculate Term Frequency for a term in a document"""
        doc = self.documents.get(doc_id)
        if not doc:
            return 0.0
        
        term_freq = doc['term_freq'].get(term, 0)
        total_terms = doc['total_terms']
        
        if total_terms == 0:
            return 0.0
        
        return term_freq / total_terms
    
    def get_idf(self, term: str) -> float:
        """Calculate Inverse Document Frequency for a term"""
        df = self.term_document_freq.get(term, 0)
        
        if df == 0:
            return 0.0
        
        return math.log(self.total_documents / df)
    
    def get_tfidf(self, doc_id: str, term: str) -> float:
        """Calculate TF-IDF score for a term in a document"""
        tf = self.get_tf(doc_id, term)
        idf = self.get_idf(term)
        return tf * idf
    
    def score_document(self, doc_id: str, query_terms: List[str]) -> float:
        """Score a document for a given query"""
        if not query_terms:
            return 0.0
        
        total_score = 0.0
        for term in query_terms:
            total_score += self.get_tfidf(doc_id, term)
        
        return total_score
    
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
            scores.append((doc_id, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    
    def get_top_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Get top documents for a query with metadata"""
        results = self.search(query)
        
        top_docs = []
        for doc_id, score in results[:limit]:
            if score > 0:
                doc_info = self.documents.get(doc_id, {})
                top_docs.append({
                    'id': doc_id,
                    'title': doc_info.get('title', ''),
                    'score': round(score, 4),
                    'total_terms': doc_info.get('total_terms', 0),
                    'unique_terms': len(doc_info.get('term_freq', {}))
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
        """Get TF-IDF statistics"""
        return {
            'total_documents': self.total_documents,
            'unique_terms': len(self.term_document_freq),
            'total_terms': sum(len(doc['terms']) for doc in self.documents.values()),
            'avg_terms_per_doc': self.total_documents > 0 and 
                sum(len(doc['terms']) for doc in self.documents.values()) / self.total_documents or 0
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
        
        for term in query_tokens:
            tf = self.get_tf(doc_id, term)
            idf = self.get_idf(term)
            tfidf = tf * idf
            
            if tfidf > 0:
                breakdown.append({
                    'term': term,
                    'tf': round(tf, 4),
                    'idf': round(idf, 4),
                    'tfidf': round(tfidf, 4),
                    'frequency': doc['term_freq'].get(term, 0)
                })
                total_score += tfidf
        
        return {
            'doc_id': doc_id,
            'title': doc['title'],
            'total_score': round(total_score, 4),
            'breakdown': breakdown,
            'query_terms': query_tokens
        }
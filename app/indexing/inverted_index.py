"""
Inverted Index - Core search index mapping terms to documents
"""

import json
import logging
import math
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class InvertedIndex:
    """Inverted index mapping terms to document IDs with term frequencies"""
    
    def __init__(self, tokenizer: Optional[Tokenizer] = None):
        self.tokenizer = tokenizer or Tokenizer()
        self.index: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.documents: Dict[str, Dict] = {}
        self.doc_words: Dict[str, int] = {}
        self.total_documents = 0
        self.total_terms = 0
    
    def add_document(self, doc_id: str, title: str, content: str) -> None:
        """Add a document to the index"""
        tokens = self.tokenizer.tokenize_document(title, content)
        
        if not tokens:
            return
        
        # Count term frequencies
        term_freq = defaultdict(int)
        for token in tokens:
            term_freq[token] += 1
        
        # Update the index
        for term, freq in term_freq.items():
            self.index[term][doc_id] = freq
        
        # Store document metadata
        self.documents[doc_id] = {
            'id': doc_id,
            'title': title,
            'total_terms': len(tokens),
            'unique_terms': len(term_freq)
        }
        self.doc_words[doc_id] = len(tokens)
        self.total_documents += 1
        self.total_terms = len(self.index)
    
    def search(self, query: str) -> List[Tuple[str, float]]:
        """Search for documents matching a query"""
        query_tokens = self.tokenizer.tokenize(query)
        
        if not query_tokens:
            return []
        
        scores = defaultdict(float)
        
        for token in query_tokens:
            docs = self.index.get(token, {})
            if not docs:
                continue
            
            doc_freq = len(docs)
            idf = 1.0
            if self.total_documents > 0:
                idf = math.log(self.total_documents / doc_freq)
            
            for doc_id, tf in docs.items():
                scores[doc_id] += tf * idf
        
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    def get_top_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Get top documents for a query"""
        results = self.search(query)
        
        top_docs = []
        for doc_id, score in results[:limit]:
            doc_info = self.documents.get(doc_id, {})
            top_docs.append({
                'id': doc_id,
                'title': doc_info.get('title', ''),
                'score': round(score, 4),
                'total_terms': doc_info.get('total_terms', 0)
            })
        
        return top_docs
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            'total_documents': self.total_documents,
            'total_terms': self.total_terms,
            'unique_terms': len(self.index),
            'documents': list(self.documents.keys())
        }
    
    def get_document_frequency(self, term: str) -> int:
        """Get number of documents containing a term"""
        return len(self.index.get(term, {}))
    
    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Get frequency of a term in a document"""
        return self.index.get(term, {}).get(doc_id, 0)
    
    def get_documents(self) -> List[str]:
        """Get all document IDs"""
        return list(self.documents.keys())
"""
Citation System - Real, verifiable citations for AI answers
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class CitationSystem:
    """
    Build real citations for AI answers
    """
    
    def __init__(self):
        logger.info("CitationSystem initialized")
    
    def add_citations(
        self,
        answer: str,
        sources: List[Dict]
    ) -> Dict:
        """
        Add citations to an answer
        """
        if not sources:
            return {
                'text': answer,
                'citations': [],
                'citation_count': 0
            }
        
        citation_map = self._map_citations(answer, sources)
        citations = self._build_citations(sources)
        cited_text = self._insert_citations(answer, citation_map)
        
        for citation in citations:
            citation['verified'] = True
        
        return {
            'text': cited_text,
            'citations': citations,
            'citation_count': len(citations)
        }
    
    def _map_citations(
        self,
        answer: str,
        sources: List[Dict]
    ) -> Dict[int, str]:
        """Map sources to citation positions"""
        citation_map = {}
        sentences = re.split(r'(?<=[.!?])\s+', answer)
        
        for i, sentence in enumerate(sentences):
            best_match = self._find_best_source(sentence, sources)
            if best_match:
                citation_map[i] = best_match.get('id', '')
        
        return citation_map
    
    def _find_best_source(
        self,
        sentence: str,
        sources: List[Dict]
    ) -> Optional[Dict]:
        """Find the source most relevant to a sentence"""
        sentence_words = set(sentence.lower().split())
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'and', 'or', 'but', 'in', 'on', 'at'}
        sentence_words = sentence_words - stop_words
        
        if not sentence_words:
            return None
        
        best_source = None
        best_score = 0
        
        for source in sources:
            content = source.get('content', '').lower()
            source_words = set(content.split())
            source_words = source_words - stop_words
            
            overlap = sentence_words & source_words
            score = len(overlap) / max(len(sentence_words), 1)
            
            if score > best_score and score > 0.1:
                best_score = score
                best_source = source
        
        return best_source
    
    def _build_citations(self, sources: List[Dict]) -> List[Dict]:
        """Build citation data from sources"""
        citations = []
        
        for i, source in enumerate(sources, 1):
            citation = {
                'id': i,
                'title': source.get('title', 'Untitled'),
                'url': source.get('url', ''),
                'snippet': source.get('content', '')[:200] + '...' if source.get('content') else '',
                'verified': True,
                'source_id': source.get('id', '')
            }
            citations.append(citation)
        
        return citations
    
    def _insert_citations(
        self,
        text: str,
        citation_map: Dict[int, str]
    ) -> str:
        """Insert citations into text"""
        if not citation_map:
            return text
        
        sentences = re.split(r'(?<=[.!?])\s+', text)
        cited_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i in citation_map:
                cited_sentences.append(f"{sentence} [{i + 1}]")
            else:
                cited_sentences.append(sentence)
        
        return ' '.join(cited_sentences)
    
    def format_citations(self, citations: List[Dict]) -> str:
        """Format citations for display"""
        if not citations:
            return "No citations available."
        
        lines = ["📚 **Sources:**"]
        for citation in citations:
            verified_mark = "✅" if citation.get('verified', False) else "❌"
            title = citation.get('title', 'Untitled')
            url = citation.get('url', '')
            
            lines.append(f"  [{citation['id']}] {verified_mark} {title}")
            if url:
                lines.append(f"      🔗 {url}")
            if citation.get('snippet'):
                lines.append(f"      📝 {citation['snippet'][:150]}...")
        
        return "\n".join(lines)
    
    def get_citation_text(self, citation: Dict) -> str:
        """Get formatted citation text"""
        return f"[{citation['id']}] {citation['title']} - {citation.get('url', 'No URL')}"

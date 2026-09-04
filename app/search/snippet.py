"""
Snippet Generator - Create highlighted text excerpts from documents
"""

import re
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class SnippetGenerator:
    """
    Generate relevant snippets from document content based on query terms
    """
    
    def __init__(
        self,
        max_snippet_length: int = 200,
        context_window: int = 30,
        max_snippets: int = 3
    ):
        self.max_snippet_length = max_snippet_length
        self.context_window = context_window
        self.max_snippets = max_snippets
    
    def generate(self, content: str, query: str) -> str:
        """
        Generate a snippet for a document based on query terms
        """
        if not content or not query:
            return content[:self.max_snippet_length] if content else ""
        
        # Tokenize query to get terms
        query_terms = self._tokenize_query(query)
        
        if not query_terms:
            return content[:self.max_snippet_length] if content else ""
        
        # Find all matches in the content
        matches = self._find_matches(content, query_terms)
        
        if not matches:
            # No matches found, return first part of content
            return self._truncate(content, self.max_snippet_length)
        
        # Extract context windows around matches
        snippets = self._extract_context_windows(content, matches)
        
        # Merge overlapping snippets
        merged_snippets = self._merge_snippets(snippets)
        
        # Combine snippets
        combined = self._combine_snippets(merged_snippets)
        
        # Highlight terms
        highlighted = self._highlight_terms(combined, query_terms)
        
        return highlighted
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize query into individual terms"""
        terms = re.findall(r'[a-zA-Z0-9]+', query.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [t for t in terms if t not in stop_words and len(t) > 1]
    
    def _find_matches(self, content: str, query_terms: List[str]) -> List[Tuple[int, int, str]]:
        """Find all occurrences of query terms in content"""
        content_lower = content.lower()
        matches = []
        
        for term in query_terms:
            start = 0
            while True:
                pos = content_lower.find(term, start)
                if pos == -1:
                    break
                if (pos == 0 or not content_lower[pos-1].isalnum()) and \
                   (pos + len(term) >= len(content_lower) or not content_lower[pos + len(term)].isalnum()):
                    matches.append((pos, pos + len(term), term))
                start = pos + 1
        
        matches.sort(key=lambda x: x[0])
        return matches
    
    def _extract_context_windows(self, content: str, matches: List[Tuple[int, int, str]]) -> List[str]:
        """Extract context windows around each match"""
        words = content.split()
        snippets = []
        
        for match_start, match_end, term in matches:
            # Find the word containing this match
            char_count = 0
            word_idx = 0
            for i, word in enumerate(words):
                if char_count + len(word) >= match_start:
                    word_idx = i
                    break
                char_count += len(word) + 1
            
            # Get context window
            start_idx = max(0, word_idx - self.context_window // 2)
            end_idx = min(len(words), word_idx + self.context_window // 2 + 1)
            
            snippet_words = words[start_idx:end_idx]
            snippet = ' '.join(snippet_words)
            snippets.append(snippet)
        
        return snippets
    
    def _merge_snippets(self, snippets: List[str]) -> List[str]:
        """Merge overlapping snippets"""
        if not snippets:
            return []
        
        # Simple deduplication
        seen = set()
        unique = []
        for s in snippets:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        
        return unique[:self.max_snippets]
    
    def _combine_snippets(self, snippets: List[str]) -> str:
        """Combine multiple snippets into one"""
        if not snippets:
            return ""
        
        if len(snippets) == 1:
            return self._truncate(snippets[0], self.max_snippet_length)
        
        combined = " ... ".join(snippets)
        return self._truncate(combined, self.max_snippet_length)
    
    def _highlight_terms(self, text: str, query_terms: List[str]) -> str:
        """Highlight query terms in the text"""
        highlighted = text
        terms = sorted(query_terms, key=len, reverse=True)
        
        for term in terms:
            pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
            highlighted = pattern.sub(f'**{term}**', highlighted)
        
        return highlighted
    
    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to max_length"""
        if len(text) <= max_length:
            return text
        
        cut_pos = text.rfind(' ', 0, max_length)
        if cut_pos == -1:
            cut_pos = max_length
        
        return text[:cut_pos] + "..."

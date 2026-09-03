"""
Tokenizer - Convert text into tokens for indexing
"""

import re
import string
from typing import List, Set


class Tokenizer:
    """Tokenizes text for indexing and searching"""
    
    # Common English stop words
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'were', 'will', 'with', 'i', 'you', 'we', 'they',
        'this', 'that', 'these', 'those', 'am', 'do', 'does', 'did',
        'have', 'had', 'has', 'my', 'your', 'our', 'their', 'him', 'her',
        'me', 'us', 'them', 'about', 'after', 'all', 'also', 'any',
        'back', 'because', 'been', 'before', 'being', 'both', 'but',
        'can', 'come', 'could', 'day', 'even', 'first', 'get', 'go',
        'good', 'great', 'how', 'into', 'like', 'long', 'make', 'many',
        'more', 'most', 'much', 'new', 'now', 'old', 'only', 'or',
        'other', 'out', 'over', 'people', 'see', 'she', 'so', 'some',
        'such', 'than', 'them', 'then', 'there', 'these', 'they',
        'think', 'time', 'too', 'two', 'up', 'upon', 'us', 'use',
        'very', 'way', 'well', 'what', 'when', 'where', 'which', 'who',
        'will', 'with', 'without', 'work', 'world', 'would', 'year'
    }
    
    def __init__(
        self, 
        lowercase: bool = True,
        remove_punctuation: bool = True,
        remove_numbers: bool = True,
        remove_stop_words: bool = True,
        min_word_length: int = 2
    ):
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation
        self.remove_numbers = remove_numbers
        self.remove_stop_words = remove_stop_words
        self.min_word_length = min_word_length
        
        # Compile regex patterns for performance
        self.punctuation_pattern = re.compile(f'[{re.escape(string.punctuation)}]')
        self.number_pattern = re.compile(r'\b\d+\b')
        self.whitespace_pattern = re.compile(r'\s+')
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into a list of tokens"""
        if not text:
            return []
        
        # Lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove punctuation
        if self.remove_punctuation:
            text = self.punctuation_pattern.sub(' ', text)
        
        # Remove numbers
        if self.remove_numbers:
            text = self.number_pattern.sub(' ', text)
        
        # Split into words
        tokens = self.whitespace_pattern.split(text.strip())
        
        # Filter tokens
        filtered_tokens = []
        for token in tokens:
            if len(token) < self.min_word_length:
                continue
            if self.remove_stop_words and token in self.STOP_WORDS:
                continue
            filtered_tokens.append(token)
        
        return filtered_tokens
    
    def tokenize_document(self, title: str, content: str) -> List[str]:
        """Tokenize a complete document (title + content)"""
        # Combine title and content with more weight on title
        combined = f"{title} {title} {title} {content}"
        return self.tokenize(combined)
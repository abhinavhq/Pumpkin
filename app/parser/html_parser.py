"""
HTML Parser - Main parser orchestrator
"""

import logging
from typing import Dict, Optional

from .cleaner import HTMLCleaner
from .extractor import ContentExtractor

logger = logging.getLogger(__name__)


class HTMLParser:
    """Main HTML parser that orchestrates cleaning and extraction"""
    
    def __init__(self):
        self.cleaner = HTMLCleaner()
        self.extractor = ContentExtractor()
    
    def parse(self, html: str, url: str = "") -> Dict:
        """
        Parse HTML and return structured content
        """
        if not html:
            logger.warning("Empty HTML provided")
            return self._empty_result(url)
        
        try:
            # Extract structured content
            extracted = self.extractor.extract_all(html)
            
            # Clean the content
            clean_text = self.cleaner.clean(html)
            
            # Combine results
            result = {
                'url': url,
                'title': extracted['title'],
                'description': extracted['description'],
                'keywords': extracted['keywords'],
                'headings': extracted['headings'],
                'paragraphs': extracted['paragraphs'],
                'main_content': extracted['main_content'],
                'clean_text': clean_text,
                'links': extracted['links'],
                'images': extracted['images'],
                'word_count': extracted['word_count'],
                'has_content': bool(extracted['paragraphs'] or extracted['main_content'])
            }
            
            logger.debug(f"Parsed {url}: {result['word_count']} words, {len(result['paragraphs'])} paragraphs")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            return self._empty_result(url)
    
    def parse_document(self, url: str, html: str) -> Dict:
        """
        Parse HTML and return document ready for indexing
        """
        parsed = self.parse(html, url)
        
        # Create document for indexing
        document = {
            'url': url,
            'title': parsed['title'],
            'content': parsed['clean_text'] or parsed['main_content'],
            'description': parsed['description'],
            'headings': parsed['headings'],
            'keywords': parsed['keywords'],
            'paragraphs': parsed['paragraphs'],
            'word_count': parsed['word_count'],
            'links': [link['url'] for link in parsed['links']],
            'has_content': parsed['has_content']
        }
        
        return document
    
    def _empty_result(self, url: str = "") -> Dict:
        """Return empty result structure"""
        return {
            'url': url,
            'title': '',
            'description': '',
            'keywords': [],
            'headings': {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []},
            'paragraphs': [],
            'main_content': '',
            'clean_text': '',
            'links': [],
            'images': [],
            'word_count': 0,
            'has_content': False
        }
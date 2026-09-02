"""
HTML Cleaner - Remove unwanted elements and normalize content
"""

import re
from typing import List, Optional
from bs4 import BeautifulSoup, NavigableString


class HTMLCleaner:
    """Clean HTML by removing unwanted elements and normalizing text"""
    
    def __init__(self):
        # Elements to remove completely
        self.remove_tags = [
            'script', 'style', 'noscript', 'iframe', 'embed',
            'object', 'applet', 'canvas', 'svg', 'math',
            'form', 'input', 'textarea', 'button', 'select',
            'nav', 'header', 'footer', 'aside', 'sidebar',
            'menu', 'menuitem', 'command', 'dialog'
        ]
        
        # Attributes to remove
        self.remove_attributes = [
            'style', 'class', 'id', 'data-*', 'on*',
            'hidden', 'aria-*', 'role'
        ]
        
        # Patterns for cleaning
        self.patterns = {
            'whitespace': re.compile(r'\s+'),
            'newlines': re.compile(r'\n+'),
        }
    
    def clean(self, html: str) -> str:
        """
        Clean HTML and return clean text content
        """
        if not html:
            return ""
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Remove unwanted tags
        self._remove_tags(soup)
        
        # Remove unwanted attributes
        self._remove_attributes(soup)
        
        # Extract text
        text = soup.get_text(separator=' ', strip=True)
        
        # Normalize whitespace
        text = self._normalize_text(text)
        
        return text
    
    def _remove_tags(self, soup: BeautifulSoup):
        """Remove unwanted HTML tags"""
        for tag in self.remove_tags:
            for element in soup.find_all(tag):
                element.decompose()
    
    def _remove_attributes(self, soup: BeautifulSoup):
        """Remove unwanted HTML attributes"""
        for tag in soup.find_all(True):
            attrs_to_remove = []
            for attr in tag.attrs:
                # Remove style, class, id, etc.
                if attr in self.remove_attributes:
                    attrs_to_remove.append(attr)
                # Remove event handlers (onclick, onload, etc.)
                elif attr.startswith('on'):
                    attrs_to_remove.append(attr)
                # Remove data-* attributes
                elif attr.startswith('data-'):
                    attrs_to_remove.append(attr)
            
            for attr in attrs_to_remove:
                del tag[attr]
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text by removing extra whitespace"""
        # Replace multiple whitespace with single space
        text = self.patterns['whitespace'].sub(' ', text)
        
        # Replace multiple newlines with single newline
        text = self.patterns['newlines'].sub('\n', text)
        
        return text.strip()
    
    def clean_metadata(self, text: str) -> str:
        """Clean metadata text"""
        if not text:
            return ""
        return ' '.join(text.split()).strip()
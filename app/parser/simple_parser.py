"""
Simple Parser - Extracts text directly from HTML
"""

import re
from bs4 import BeautifulSoup


class SimpleParser:
    """Simple HTML text extractor"""
    
    def parse(self, html: str) -> dict:
        """Extract text from HTML"""
        if not html:
            return {'title': 'No Title', 'content': '', 'word_count': 0}
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Get title
            title = "No Title"
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                # Remove suffix like " - Wikipedia"
                title = re.sub(r'\s*[-–]\s*Wikipedia.*$', '', title)
            
            # Remove unwanted tags
            for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Get all text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean text
            text = re.sub(r'\[\d+\]', '', text)  # Remove citation numbers
            text = re.sub(r'\s+', ' ', text)      # Remove extra spaces
            text = text.strip()
            
            # Take first 5000 characters
            content = text[:5000]
            word_count = len(content.split())
            
            return {
                'title': title,
                'content': content,
                'word_count': word_count,
                'has_content': word_count > 30
            }
            
        except Exception as e:
            print(f"Parser error: {e}")
            return {'title': 'Error', 'content': '', 'word_count': 0}
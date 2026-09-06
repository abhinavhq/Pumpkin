"""
Wikipedia Parser - Ultra Simple
"""

import re
from bs4 import BeautifulSoup


class WikipediaParser:
    """Parse Wikipedia pages to extract clean content"""
    
    def parse(self, html: str) -> dict:
        """Parse Wikipedia HTML and extract content"""
        if not html:
            return {'title': 'No Title', 'content': '', 'word_count': 0}
        
        try:
            soup = BeautifulSoup(html, 'lxml')
            
            # Get title
            title_tag = soup.find('h1', {'id': 'firstHeading'})
            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            
            # Find all paragraphs
            paragraphs = []
            
            # Look for content in mw-parser-output
            content_div = soup.find('div', {'class': 'mw-parser-output'})
            
            if content_div:
                # Remove tables, references, etc.
                for tag in content_div.find_all(['table', 'div.reflist', 'span.mw-editsection']):
                    tag.decompose()
                
                # Get all paragraphs
                for p in content_div.find_all('p'):
                    text = p.get_text(strip=True)
                    # Remove citation numbers
                    text = re.sub(r'\[\d+\]', '', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    if text and len(text) > 30:
                        paragraphs.append(text)
            
            # If no paragraphs found, try to get text from the whole page
            if not paragraphs:
                # Find the main content
                main_content = soup.find('div', {'id': 'mw-content-text'})
                if main_content:
                    text = main_content.get_text(strip=True)
                    text = re.sub(r'\[\d+\]', '', text)
                    text = re.sub(r'\s+', ' ', text).strip()
                    # Take first 2000 characters
                    if text:
                        paragraphs = [text[:2000]]
            
            content = ' '.join(paragraphs[:10])
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
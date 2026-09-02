"""
Content Extractor - Extract structured content from HTML
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class ContentExtractor:
    """Extract structured content from HTML"""
    
    def __init__(self):
        self.headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    def extract_all(self, html: str) -> Dict:
        """
        Extract all content from HTML
        """
        if not html:
            return self._empty_result()
        
        soup = BeautifulSoup(html, 'lxml')
        
        result = {
            'title': self.extract_title(soup),
            'headings': self.extract_headings(soup),
            'description': self.extract_description(soup),
            'keywords': self.extract_keywords(soup),
            'paragraphs': self.extract_paragraphs(soup),
            'main_content': self.extract_main_content(soup),
            'links': self.extract_links(soup),
            'images': self.extract_images(soup),
            'word_count': 0,
        }
        
        # Count words
        content = ' '.join(result['paragraphs'])
        result['word_count'] = len(content.split())
        
        return result
    
    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try <title> tag
        title_tag = soup.find('title')
        if title_tag and title_tag.string:
            return title_tag.string.strip()
        
        # Try Open Graph title
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        # Try first h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        return "No Title"
    
    def extract_headings(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract all headings grouped by level"""
        result = {f'h{i}': [] for i in range(1, 7)}
        
        for tag in self.headings:
            elements = soup.find_all(tag)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text:
                    result[tag].append(text)
        
        return result
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        # Try standard meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        return ""
    
    def extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract meta keywords"""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords['content'].split(',')
            return [k.strip() for k in keywords if k.strip()]
        return []
    
    def extract_paragraphs(self, soup: BeautifulSoup) -> List[str]:
        """Extract all paragraphs"""
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text(strip=True)
            if text and len(text) > 10:  # Filter very short text
                paragraphs.append(text)
        return paragraphs
    
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content"""
        # Try article tag
        article = soup.find('article')
        if article:
            return article.get_text(separator=' ', strip=True)
        
        # Try main tag
        main = soup.find('main')
        if main:
            return main.get_text(separator=' ', strip=True)
        
        # Try content divs
        content_selectors = [
            'div[class*="content"]',
            'div[class*="article"]',
            'div[class*="post"]',
            'div[class*="entry"]',
            'div[id*="content"]',
            'div[id*="article"]',
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(separator=' ', strip=True)
                if len(text) > 100:
                    return text
        
        # Fallback: all body text
        body = soup.find('body')
        if body:
            # Remove header, footer, nav, aside
            for tag in ['header', 'footer', 'nav', 'aside']:
                for elem in body.find_all(tag):
                    elem.decompose()
            return body.get_text(separator=' ', strip=True)
        
        # Ultimate fallback
        return soup.get_text(separator=' ', strip=True)
    
    def extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links with their text"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                links.append({
                    'url': href,
                    'text': text[:100] if text else ''
                })
        return links[:100]  # Limit to 100 links
    
    def extract_images(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract images with alt text"""
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            alt = img.get('alt', '')
            if src:
                images.append({
                    'src': src,
                    'alt': alt[:100] if alt else ''
                })
        return images[:20]  # Limit to 20 images
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'title': '',
            'headings': {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []},
            'description': '',
            'keywords': [],
            'paragraphs': [],
            'main_content': '',
            'links': [],
            'images': [],
            'word_count': 0,
        }

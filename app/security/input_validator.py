"""
Input Validator - Sanitize and validate user input
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Validate and sanitize user input
    """
    
    def __init__(self):
        self.dangerous_chars = re.compile(r'[<>"\'();&+]')
        self.max_query_length = 500
        self.min_query_length = 1
        
        self.blocked_patterns = [
            r'(?i)\b(select|insert|update|delete|drop|alter|create)\b',
            r'(?i)\b(union|join|where|from|into|values)\b',
            r'(?i)\b(exec|execute|sp_|xp_|shell|cmd)\b',
            r'(?i)\b(--|;|\|\||&&|\b(and|or)\b)',
        ]
    
    def sanitize_query(self, query: str) -> Optional[str]:
        if not query:
            return None
        
        query = query.strip()
        
        if len(query) > self.max_query_length:
            logger.warning(f"Query too long: {len(query)} chars")
            return None
        
        if len(query) < self.min_query_length:
            return None
        
        query = self.dangerous_chars.sub(' ', query)
        
        for pattern in self.blocked_patterns:
            if re.search(pattern, query):
                logger.warning(f"Blocked query pattern: {query[:50]}")
                return None
        
        query = ' '.join(query.split())
        return query
    
    def validate_url(self, url: str) -> bool:
        if not url:
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        internal_ips = [
            '127.0.0.1', 'localhost', '0.0.0.0',
            '10.', '172.16.', '172.17.', '172.18.', '172.19.',
            '172.20.', '172.21.', '172.22.', '172.23.',
            '172.24.', '172.25.', '172.26.', '172.27.',
            '172.28.', '172.29.', '172.30.', '172.31.',
            '192.168.', '169.254.'
        ]
        
        url_lower = url.lower()
        for ip in internal_ips:
            if url_lower.startswith(('http://' + ip, 'https://' + ip)):
                logger.warning(f"Blocked internal IP: {url}")
                return False
        
        dangerous_schemes = ['file://', 'gopher://', 'ftp://', 'dict://']
        for scheme in dangerous_schemes:
            if url_lower.startswith(scheme):
                logger.warning(f"Blocked dangerous scheme: {url}")
                return False
        
        return True
    
    def sanitize_html(self, text: str) -> str:
        if not text:
            return ""
        
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        text = text.replace('/', '&#x2F;')
        
        return text

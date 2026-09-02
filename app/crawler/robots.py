"""
Robots.txt Parser - Respect website crawling rules
"""

import logging
from urllib.parse import urlparse
from typing import Optional, Dict

import httpx

logger = logging.getLogger(__name__)


class RobotsParser:
    """Parse and check robots.txt rules"""
    
    def __init__(self, user_agent: str = "AISearchBot/1.0"):
        self.user_agent = user_agent
        self.rules_cache: Dict[str, Dict] = {}
    
    async def fetch_robots(self, domain: str) -> Optional[str]:
        """Fetch robots.txt from domain"""
        robots_url = f"https://{domain}/robots.txt"
        
        try:
            # Create a new client for each request to avoid issues
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(robots_url)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            logger.debug(f"Failed to fetch robots.txt for {domain}: {e}")
        
        return None
    
    async def parse_robots(self, domain: str) -> Dict:
        """Parse robots.txt and extract rules"""
        if domain in self.rules_cache:
            return self.rules_cache[domain]
        
        robots_text = await self.fetch_robots(domain)
        rules = {
            "allow": [],
            "disallow": [],
            "crawl_delay": None,
            "sitemap": None,
            "user_agent_matched": False
        }
        
        if not robots_text:
            self.rules_cache[domain] = rules
            return rules
        
        current_agent = None
        lines = robots_text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "user-agent":
                    current_agent = value
                    # Check if this user-agent matches ours
                    if current_agent == "*" or current_agent.lower() == self.user_agent.lower():
                        rules["user_agent_matched"] = True
                
                # Only apply rules that match our user agent
                if rules["user_agent_matched"] or current_agent == "*":
                    if key == "allow":
                        rules["allow"].append(value)
                    elif key == "disallow":
                        rules["disallow"].append(value)
                    elif key == "crawl-delay" and value:
                        try:
                            rules["crawl_delay"] = float(value)
                        except ValueError:
                            pass
                    elif key == "sitemap":
                        rules["sitemap"] = value
        
        self.rules_cache[domain] = rules
        return rules
    
    async def can_crawl(self, url: str) -> bool:
        """Check if a URL can be crawled according to robots.txt"""
        try:
            domain = urlparse(url).netloc
            rules = await self.parse_robots(domain)
            
            # If no rules or no disallow, allow
            if not rules["disallow"]:
                return True
            
            # Check if URL is disallowed
            for pattern in rules["disallow"]:
                if pattern and pattern in url:
                    return False
            
            # Check if URL is explicitly allowed
            for pattern in rules["allow"]:
                if pattern and pattern in url:
                    return True
            
            return True
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True  # Allow by default if there's an error
    
    def get_crawl_delay(self, url: str) -> Optional[float]:
        """Get crawl delay for a URL's domain"""
        try:
            domain = urlparse(url).netloc
            if domain in self.rules_cache:
                return self.rules_cache[domain].get("crawl_delay")
        except Exception:
            pass
        return None
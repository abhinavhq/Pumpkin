"""
Web Crawler - Asynchronous crawler with robots.txt support
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import httpx

from .url_utils import (
    normalize_url, 
    is_valid_url, 
    resolve_relative_url,
    get_domain,
    is_html_content
)
from .robots import RobotsParser
from .url_queue import URLQueue

logger = logging.getLogger(__name__)


class Crawler:
    """Asynchronous web crawler with robots.txt support"""
    
    def __init__(
        self,
        user_agent: str = "AISearchBot/1.0",
        max_pages: int = 100,
        max_depth: int = 3,
        timeout: int = 30,
        delay: float = 1.0,
        max_response_size: int = 10 * 1024 * 1024,  # 10MB
        max_queue_size: int = 10000,
        allowed_domains: Optional[List[str]] = None
    ):
        self.user_agent = user_agent
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.delay = delay
        self.max_response_size = max_response_size
        self.allowed_domains = allowed_domains
        
        self.queue = URLQueue(max_queue_size)
        self.robots = RobotsParser(user_agent)
        self.client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": user_agent}
        )
        
        self.crawled_data: List[Dict[str, Any]] = []
        self.total_pages = 0
        self.failed_pages = 0
    
    async def crawl(self, seed_urls: List[str]) -> List[Dict[str, Any]]:
        """
        Start crawling from seed URLs
        """
        logger.info(f"Starting crawler with {len(seed_urls)} seed URLs")
        logger.info(f"Max pages: {self.max_pages}, Max depth: {self.max_depth}")
        
        # Add seed URLs to queue
        added_count = 0
        for url in seed_urls:
            if is_valid_url(url):
                await self.queue.add(url)
                added_count += 1
            else:
                logger.warning(f"Invalid seed URL: {url}")
        
        logger.info(f"Added {added_count} seed URLs to queue")
        
        # Start crawling
        await self._crawl_loop()
        
        logger.info(f"Crawling complete. Pages: {self.total_pages}, Failed: {self.failed_pages}")
        return self.crawled_data
    
    async def _crawl_loop(self):
        """Main crawling loop"""
        while self.queue.size > 0 and self.total_pages < self.max_pages:
            url = await self.queue.get()
            
            if not url:
                continue
            
            # Check domain restrictions
            if self.allowed_domains:
                domain = get_domain(url)
                if domain not in self.allowed_domains:
                    logger.debug(f"Skipping {url} (domain not allowed)")
                    await self.queue.mark_visited(url)
                    continue
            
            # Check robots.txt
            if not await self.robots.can_crawl(url):
                logger.info(f"Skipping {url} (robots.txt disallows)")
                await self.queue.mark_visited(url)
                continue
            
            # Crawl the URL
            await self._crawl_url(url)
            
            # Rate limiting
            crawl_delay = self.robots.get_crawl_delay(url)
            delay = crawl_delay if crawl_delay else self.delay
            await asyncio.sleep(min(delay, 10.0))  # Max 10 seconds
    
    async def _crawl_url(self, url: str):
        """Crawl a single URL"""
        logger.info(f"Crawling: {url}")
        
        try:
            response = await self.client.get(url)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: Status {response.status_code}")
                self.failed_pages += 1
                await self.queue.mark_visited(url)
                return
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if not is_html_content(content_type):
                logger.debug(f"Skipping {url}: Not HTML ({content_type})")
                self.failed_pages += 1
                await self.queue.mark_visited(url)
                return
            
            # Check response size
            if len(response.content) > self.max_response_size:
                logger.warning(f"Response too large for {url}: {len(response.content)} bytes")
                self.failed_pages += 1
                await self.queue.mark_visited(url)
                return
            
            # Get HTML content
            html_content = response.text
            
            # Extract links (basic version)
            links = self._extract_links(url, html_content)
            
            # Add new links to queue (limit to prevent explosion)
            new_links = []
            for link in links[:100]:  # Max 100 links per page
                if is_valid_url(link) and self.total_pages + len(new_links) < self.max_pages:
                    new_links.append(link)
            
            added = await self.queue.add_multiple(new_links)
            logger.debug(f"Added {added} new links from {url}")
            
            # Extract title (basic version)
            title = self._extract_title(html_content)
            
            # Save data
            data = {
                "url": url,
                "title": title,
                "content": html_content[:5000],  # Store first 5000 chars for now
                "timestamp": datetime.utcnow().isoformat(),
                "status_code": response.status_code,
                "links_count": len(links),
                "content_size": len(html_content)
            }
            self.crawled_data.append(data)
            self.total_pages += 1
            
            await self.queue.mark_visited(url)
            logger.info(f"✅ Successfully crawled {url} (Page {self.total_pages})")
            
        except httpx.TimeoutException:
            logger.error(f"Timeout crawling {url}")
            self.failed_pages += 1
            await self.queue.mark_visited(url)
        except httpx.HTTPError as e:
            logger.error(f"HTTP error crawling {url}: {e}")
            self.failed_pages += 1
            await self.queue.mark_visited(url)
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            self.failed_pages += 1
            await self.queue.mark_visited(url)
    
    def _extract_links(self, url: str, html: str) -> List[str]:
        """
        Extract links from HTML (basic version)
        Will be improved in Phase 3 with BeautifulSoup
        """
        links = []
        start_pos = 0
        
        # Find all href attributes
        while True:
            # Look for href="..."
            href_start = html.find('href="', start_pos)
            if href_start == -1:
                # Try href='...'
                href_start = html.find("href='", start_pos)
                if href_start == -1:
                    break
                href_start += 6
                href_end = html.find("'", href_start)
            else:
                href_start += 6
                href_end = html.find('"', href_start)
            
            if href_end == -1:
                break
            
            link = html[href_start:href_end]
            
            # Filter out empty, javascript, mailto, anchor-only links
            if link and not link.startswith("#") and not link.startswith("javascript:"):
                if not link.startswith("mailto:") and not link.startswith("tel:"):
                    # Convert relative to absolute
                    if link.startswith("/") or not link.startswith("http"):
                        link = resolve_relative_url(url, link)
                    
                    if is_valid_url(link):
                        links.append(link)
            
            start_pos = href_end + 1
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            normalized = normalize_url(link)
            if normalized not in seen:
                seen.add(normalized)
                unique_links.append(link)
        
        return unique_links
    
    def _extract_title(self, html: str) -> str:
        """Extract title from HTML (basic version)"""
        # Look for <title>
        title_start = html.lower().find("<title>")
        if title_start == -1:
            # Try uppercase
            title_start = html.find("<TITLE>")
            if title_start == -1:
                return "No Title"
        
        title_start = html.find(">", title_start) + 1
        title_end = html.lower().find("</title>", title_start)
        if title_end == -1:
            title_end = html.find("</TITLE>", title_start)
            if title_end == -1:
                return "No Title"
        
        title = html[title_start:title_end].strip()
        return title if title else "No Title"
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()
        logger.info("Crawler closed")
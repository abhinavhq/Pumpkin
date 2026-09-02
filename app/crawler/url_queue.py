"""
URL Queue - Manage URLs to crawl with deduplication
"""

import asyncio
from collections import deque
from typing import Set, Optional, List
import logging

from .url_utils import normalize_url

logger = logging.getLogger(__name__)


class URLQueue:
    """Thread-safe URL queue with deduplication"""
    
    def __init__(self, max_size: int = 10000):
        self.queue = deque()
        self.visited: Set[str] = set()
        self.pending: Set[str] = set()
        self.max_size = max_size
        self._lock = asyncio.Lock()
    
    async def add(self, url: str) -> bool:
        """
        Add URL to queue if not visited or pending.
        Returns True if added, False if duplicate.
        """
        if not url:
            return False
        
        normalized = normalize_url(url)
        
        async with self._lock:
            if normalized in self.visited or normalized in self.pending:
                return False
            
            if len(self.queue) >= self.max_size:
                logger.warning(f"Queue at max size ({self.max_size}), rejecting {url}")
                return False
            
            self.pending.add(normalized)
            self.queue.append(normalized)
            logger.debug(f"Added to queue: {url}")
            return True
    
    async def add_multiple(self, urls: List[str]) -> int:
        """Add multiple URLs to queue. Returns count added."""
        count = 0
        for url in urls:
            if await self.add(url):
                count += 1
        return count
    
    async def get(self) -> Optional[str]:
        """Get next URL from queue"""
        async with self._lock:
            if not self.queue:
                return None
            
            url = self.queue.popleft()
            self.pending.discard(url)
            return url
    
    async def mark_visited(self, url: str):
        """Mark URL as visited"""
        normalized = normalize_url(url)
        async with self._lock:
            self.visited.add(normalized)
            self.pending.discard(normalized)
    
    async def is_visited(self, url: str) -> bool:
        """Check if URL has been visited"""
        normalized = normalize_url(url)
        async with self._lock:
            return normalized in self.visited
    
    async def clear(self):
        """Clear all queues"""
        async with self._lock:
            self.queue.clear()
            self.pending.clear()
            self.visited.clear()
    
    @property
    def size(self) -> int:
        return len(self.queue)
    
    @property
    def visited_count(self) -> int:
        return len(self.visited)
    
    @property
    def pending_count(self) -> int:
        return len(self.pending)
    
    def __len__(self):
        return self.size
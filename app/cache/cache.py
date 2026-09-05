"""
Cache - LRU Cache with TTL for search results
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from collections import OrderedDict
from functools import wraps

logger = logging.getLogger(__name__)


class LRUCache:
    """
    LRU Cache with Time-To-Live (TTL)
    """
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.hits = 0
        self.misses = 0
        
        logger.info(f"LRUCache initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            self.misses += 1
            return None
        
        if time.time() - self.timestamps[key] > self.ttl:
            self._remove(key)
            self.misses += 1
            return None
        
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        if key in self.cache:
            self._remove(key)
        
        if len(self.cache) >= self.max_size:
            oldest = next(iter(self.cache))
            self._remove(oldest)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def _remove(self, key: str) -> None:
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]
    
    def clear(self) -> None:
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 4),
            'ttl_seconds': self.ttl
        }


def cached(ttl_seconds: int = 300):
    """
    Decorator for caching function results
    """
    def decorator(func: Callable):
        cache = LRUCache(max_size=100, ttl_seconds=ttl_seconds)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}_{args}_{kwargs}"
            key = key.replace(' ', '_')
            
            result = cache.get(key)
            if result is not None:
                return result
            
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        wrapper.cache = cache
        return wrapper
    
    return decorator

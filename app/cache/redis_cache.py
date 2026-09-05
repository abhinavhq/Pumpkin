"""
Redis Cache - Fast in-memory caching for search results
"""

import json
import logging
import time
from typing import Optional, Dict, Any
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache for search results
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl_seconds: int = 300,
        use_memory_cache: bool = True
    ):
        self.ttl = ttl_seconds
        self.use_memory_cache = use_memory_cache
        self.memory_cache = {}
        self.hits = 0
        self.misses = 0
        
        self.redis_client = None
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self.redis_client.ping()
                logger.info(f"Redis connected: {host}:{port}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                if use_memory_cache:
                    logger.info("Using in-memory cache as fallback")
                self.redis_client = None
        else:
            logger.info("Redis not installed. Using in-memory cache.")
        
        logger.info("RedisCache initialized")
    
    def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    self.hits += 1
                    return json.loads(value)
            except Exception as e:
                logger.debug(f"Redis get error: {e}")
        
        if self.use_memory_cache:
            if key in self.memory_cache:
                data, timestamp = self.memory_cache[key]
                if time.time() - timestamp < self.ttl:
                    self.hits += 1
                    return data
                else:
                    del self.memory_cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any) -> bool:
        try:
            serialized = json.dumps(value)
        except:
            serialized = str(value)
        
        success = False
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, self.ttl, serialized)
                success = True
            except Exception as e:
                logger.debug(f"Redis set error: {e}")
        
        if self.use_memory_cache:
            self.memory_cache[key] = (value, time.time())
            if len(self.memory_cache) > 1000:
                oldest_key = next(iter(self.memory_cache))
                del self.memory_cache[oldest_key]
            success = True
        
        return success
    
    def delete(self, key: str) -> bool:
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass
        
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        return True
    
    def clear(self) -> bool:
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except:
                pass
        
        self.memory_cache.clear()
        return True
    
    def get_stats(self) -> Dict:
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate * 100, 2),
            'total_requests': total,
            'memory_cache_size': len(self.memory_cache),
            'redis_available': self.redis_client is not None
        }

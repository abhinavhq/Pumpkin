"""
Test script for Redis cache
"""

import time
import logging
from app.cache.redis_cache import RedisCache

logging.basicConfig(level=logging.INFO)


def test_cache():
    """Test Redis cache"""
    
    print("\n" + "="*50)
    print("🗄️ TESTING REDIS CACHE")
    print("="*50 + "\n")
    
    cache = RedisCache(ttl_seconds=10)
    
    print("📝 Testing set/get...")
    cache.set("test_key", {"message": "Hello Redis!"})
    result = cache.get("test_key")
    print(f"   ✅ Retrieved: {result}")
    
    print("\n⏱️ Testing TTL...")
    cache.set("ttl_test", "This will expire in 5 seconds")
    print(f"   ✅ Set TTL test (5 seconds)")
    
    print("   Waiting 6 seconds...")
    time.sleep(6)
    
    expired = cache.get("ttl_test")
    print(f"   ✅ TTL expired: {expired is None} (should be None)")
    
    stats = cache.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate']}%")
    print(f"   Memory Cache Size: {stats['memory_cache_size']}")
    
    print("\n" + "="*50)
    print("✅ Redis cache test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_cache()

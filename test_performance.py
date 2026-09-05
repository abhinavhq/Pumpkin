"""
Test script for performance optimization
"""

import logging
from app.cache.cache import LRUCache, cached
from app.performance.benchmark import Benchmark
from app.retrieval.hybrid import HybridSearch

logging.basicConfig(level=logging.INFO)


def test_lru_cache():
    print("\n" + "="*50)
    print("TESTING LRU CACHE")
    print("="*50 + "\n")
    
    cache = LRUCache(max_size=3, ttl_seconds=10)
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")
    
    print("Added 3 items to cache")
    print(f"   Cache size: {len(cache.cache)}")
    
    print("\nRetrieving items:")
    print(f"   key1: {cache.get('key1')}")
    print(f"   key2: {cache.get('key2')}")
    print(f"   key3: {cache.get('key3')}")
    
    print("\nAdding 4th item (should evict oldest)...")
    cache.set("key4", "value4")
    print(f"   Cache size: {len(cache.cache)}")
    print(f"   key1 exists: {cache.get('key1') is not None} (should be None)")
    
    stats = cache.get_stats()
    print(f"\nCache Stats:")
    print(f"   Size: {stats['size']}/{stats['max_size']}")
    print(f"   Hits: {stats['hits']}")
    print(f"   Misses: {stats['misses']}")
    print(f"   Hit Rate: {stats['hit_rate']*100:.1f}%")
    
    print("\n" + "="*50)
    print("LRU cache test complete!")
    print("="*50 + "\n")


@cached(ttl_seconds=30)
def expensive_function(query: str) -> str:
    import time
    time.sleep(0.1)
    return f"Result for: {query}"


def test_cached_decorator():
    print("\n" + "="*50)
    print("TESTING CACHED DECORATOR")
    print("="*50 + "\n")
    
    query = "python programming"
    
    print("First call (should be slow):")
    import time
    start = time.time()
    result1 = expensive_function(query)
    elapsed1 = (time.time() - start) * 1000
    print(f"   Result: {result1}")
    print(f"   Time: {elapsed1:.2f}ms")
    
    print("\nSecond call (should be fast - cached):")
    start = time.time()
    result2 = expensive_function(query)
    elapsed2 = (time.time() - start) * 1000
    print(f"   Result: {result2}")
    print(f"   Time: {elapsed2:.2f}ms")
    
    stats = expensive_function.cache.get_stats()
    print(f"\nCache Stats:")
    print(f"   Size: {stats['size']}/{stats['max_size']}")
    print(f"   Hit Rate: {stats['hit_rate']*100:.1f}%")
    
    print("\n" + "="*50)
    print("Cached decorator test complete!")
    print("="*50 + "\n")


def test_benchmark():
    print("\n" + "="*50)
    print("TESTING BENCHMARK")
    print("="*50 + "\n")
    
    benchmark = Benchmark()
    
    def slow_search(query: str) -> str:
        import time
        time.sleep(0.05)
        return f"Result: {query}"
    
    queries = ["python", "search", "web", "data", "machine"]
    results = benchmark.run_benchmark(slow_search, queries, iterations=3)
    
    print(f"Results:")
    print(f"   Min: {results['min']}ms")
    print(f"   Max: {results['max']}ms")
    print(f"   Mean: {results['mean']}ms")
    print(f"   Median: {results['median']}ms")
    print(f"   StdDev: {results['stddev']}ms")
    
    print("\n" + "="*50)
    print("Benchmark test complete!")
    print("="*50 + "\n")


def test_real_search_benchmark():
    print("\n" + "="*50)
    print("BENCHMARKING REAL SEARCH ENGINE")
    print("="*50 + "\n")
    
    hybrid = HybridSearch(weight_bm25=0.5, weight_semantic=0.5)
    
    docs = [
        {'id': 'doc1', 'title': 'Python Programming', 'content': 'Python is a versatile programming language.'},
        {'id': 'doc2', 'title': 'Search Engine Basics', 'content': 'Search engines use algorithms to find documents.'},
        {'id': 'doc3', 'title': 'Web Development', 'content': 'Web development with Python is popular.'},
    ]
    
    for doc in docs:
        hybrid.add_document(doc['id'], doc['title'], doc['content'])
    
    benchmark = Benchmark()
    queries = ["python", "search engine", "web development", "programming language"]
    
    print(f"Benchmarking hybrid search with {len(queries)} queries...")
    
    results = benchmark.run_benchmark(
        lambda q: hybrid.get_top_documents(q, limit=5),
        queries,
        iterations=3
    )
    
    print(f"\nResults:")
    print(f"   Min: {results['min']:.2f}ms")
    print(f"   Max: {results['max']:.2f}ms")
    print(f"   Mean: {results['mean']:.2f}ms")
    print(f"   Median: {results['median']:.2f}ms")
    print(f"   StdDev: {results['stddev']:.2f}ms")
    
    print("\n" + "="*50)
    print("Real search benchmark complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_lru_cache()
    test_cached_decorator()
    test_benchmark()
    test_real_search_benchmark()

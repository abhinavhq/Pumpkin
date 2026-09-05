"""
Benchmark - Measure search performance
"""

import time
import logging
from typing import List, Dict, Callable
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class Benchmark:
    """
    Benchmark search performance
    """
    
    def __init__(self):
        self.results = []
    
    def measure(self, func: Callable, *args, **kwargs) -> float:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = (time.time() - start) * 1000
        return elapsed, result
    
    def run_benchmark(
        self,
        func: Callable,
        queries: List[str],
        iterations: int = 5
    ) -> Dict:
        times = []
        
        for query in queries:
            for _ in range(iterations):
                elapsed, _ = self.measure(func, query)
                times.append(elapsed)
        
        return {
            'min': round(min(times), 2),
            'max': round(max(times), 2),
            'mean': round(mean(times), 2),
            'median': round(median(times), 2),
            'stddev': round(stdev(times), 2) if len(times) > 1 else 0,
            'total_measurements': len(times)
        }
    
    def compare_engines(
        self,
        engines: Dict[str, Callable],
        queries: List[str],
        iterations: int = 3
    ) -> Dict:
        results = {}
        
        for name, func in engines.items():
            logger.info(f"Benchmarking: {name}")
            results[name] = self.run_benchmark(func, queries, iterations)
        
        return results
    
    def print_report(self, results: Dict):
        print("\n" + "="*60)
        print("⚡ PERFORMANCE BENCHMARK REPORT")
        print("="*60 + "\n")
        
        print(f"{'Engine':<15} {'Mean (ms)':<15} {'Median (ms)':<15} {'StdDev':<10}")
        print("-"*60)
        
        for name, stats in results.items():
            print(f"{name:<15} {stats['mean']:<15} {stats['median']:<15} {stats['stddev']:<10}")
        
        print("\n" + "="*60)
        print("✅ Benchmark complete!")
        print("="*60 + "\n")

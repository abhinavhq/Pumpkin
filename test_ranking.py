"""
Test script for advanced ranking
"""

import logging
from datetime import datetime, timedelta
from app.ranking.ranker import AdvancedRanker

logging.basicConfig(level=logging.INFO)


def test_advanced_ranking():
    """Test advanced ranking with various signals"""
    
    print("\n" + "="*50)
    print("📊 TESTING ADVANCED RANKING")
    print("="*50 + "\n")
    
    ranker = AdvancedRanker(
        weight_bm25=0.30,
        weight_title=0.25,
        weight_heading=0.20,
        weight_freshness=0.15,
        weight_domain=0.10
    )
    
    query = "python programming"
    query_tokens = ["python", "programming"]
    
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide 2024',
            'content': 'Python is a versatile programming language...',
            'headings': {'h1': ['Python Guide'], 'h2': ['Getting Started']},
            'created_at': datetime.now() - timedelta(days=5),
            'url': 'https://python.org/guide',
            'bm25_score': 0.85
        },
        {
            'id': 'doc2',
            'title': 'About Our Company',
            'content': 'We use Python programming for our services...',
            'headings': {'h1': ['About Us'], 'h2': ['Our Services']},
            'created_at': datetime.now() - timedelta(days=100),
            'url': 'https://example.com/about',
            'bm25_score': 0.75
        },
        {
            'id': 'doc3',
            'title': 'JavaScript Tutorial',
            'content': 'This is about Python programming in web development...',
            'headings': {'h1': ['JavaScript'], 'h2': ['Tutorial']},
            'created_at': datetime.now() - timedelta(days=365),
            'url': 'https://example.com/js',
            'bm25_score': 0.60
        },
        {
            'id': 'doc4',
            'title': 'Python for Data Science',
            'content': 'Python programming is essential for data science...',
            'headings': {'h1': ['Data Science'], 'h2': ['Python']},
            'created_at': datetime.now() - timedelta(days=30),
            'url': 'https://medium.com/data-science',
            'bm25_score': 0.70
        }
    ]
    
    print("📄 Ranking Documents for query: 'python programming'\n")
    print("-" * 60)
    
    ranked = ranker.rank(query, query_tokens, documents)
    
    for i, (doc_id, score, signals) in enumerate(ranked, 1):
        doc = next(d for d in documents if d['id'] == doc_id)
        print(f"\n{i}. {doc['title']}")
        print(f"   Final Score: {score:.4f}")
        print(f"   Signals:")
        print(f"     - BM25: {signals['bm25']:.4f}")
        print(f"     - Title: {signals['title']:.4f}")
        print(f"     - Heading: {signals['heading']:.4f}")
        print(f"     - Freshness: {signals['freshness']:.4f}")
        print(f"     - Domain: {signals['domain']:.4f}")
    
    print("\n" + "="*50)
    print("✅ Advanced ranking test complete!")
    print("="*50 + "\n")


def test_weight_comparison():
    """Test different weight configurations"""
    
    print("\n" + "="*50)
    print("⚖️ WEIGHT COMPARISON")
    print("="*50 + "\n")
    
    configs = [
        ("Balanced", 0.30, 0.25, 0.20, 0.15, 0.10),
        ("BM25 Focus", 0.60, 0.15, 0.10, 0.10, 0.05),
        ("Title Focus", 0.15, 0.50, 0.15, 0.10, 0.10),
        ("Freshness Focus", 0.20, 0.20, 0.15, 0.35, 0.10),
    ]
    
    query = "python programming"
    query_tokens = ["python", "programming"]
    
    docs = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide',
            'content': 'Python is versatile...',
            'headings': {'h1': ['Python Guide']},
            'created_at': datetime.now() - timedelta(days=1),
            'url': 'https://python.org/guide',
            'bm25_score': 0.90
        },
        {
            'id': 'doc2',
            'title': 'Old Company Page',
            'content': 'Python programming used...',
            'headings': {'h1': ['About']},
            'created_at': datetime.now() - timedelta(days=800),
            'url': 'https://example.com/old',
            'bm25_score': 0.80
        }
    ]
    
    for name, w1, w2, w3, w4, w5 in configs:
        ranker = AdvancedRanker(
            weight_bm25=w1, weight_title=w2,
            weight_heading=w3, weight_freshness=w4,
            weight_domain=w5
        )
        
        results = ranker.rank(query, query_tokens, docs)
        
        print(f"\n📊 {name}:")
        print(f"   Weights: BM25={w1}, Title={w2}, Heading={w3}, Freshness={w4}, Domain={w5}")
        
        for doc_id, score, _ in results:
            doc = next(d for d in docs if d['id'] == doc_id)
            print(f"   - {doc['title']}: {score:.4f}")


if __name__ == "__main__":
    test_advanced_ranking()
    test_weight_comparison()

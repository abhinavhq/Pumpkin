"""
Test script for hybrid search
"""

import logging
from app.retrieval.hybrid import HybridSearch

# Set up logging
logging.basicConfig(level=logging.INFO)


def test_hybrid_search():
    """Test hybrid search"""
    
    print("\n" + "="*50)
    print("🔀 TESTING HYBRID SEARCH")
    print("="*50 + "\n")
    
    # Create hybrid search with balanced weights
    hybrid = HybridSearch(weight_bm25=0.5, weight_semantic=0.5)
    
    # Sample documents
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide',
            'content': 'Python is a versatile programming language. Python is great for beginners.'
        },
        {
            'id': 'doc2',
            'title': 'Search Engine Basics',
            'content': 'Search engines use inverted indexes and ranking algorithms to find relevant documents.'
        },
        {
            'id': 'doc3',
            'title': 'Web Development with Python',
            'content': 'Web development involves building websites and web applications with Python.'
        },
        {
            'id': 'doc4',
            'title': 'Data Science with Python',
            'content': 'Data science uses programming and statistics to find insights in data.'
        },
        {
            'id': 'doc5',
            'title': 'Machine Learning',
            'content': 'Machine learning is a subset of artificial intelligence that uses data to train models.'
        }
    ]
    
    print("📄 Adding documents to hybrid index...\n")
    for doc in documents:
        hybrid.add_document(doc['id'], doc['title'], doc['content'])
        print(f"   ✅ Added: {doc['title']}")
    
    stats = hybrid.get_stats()
    print(f"\n📊 Hybrid Search Stats:")
    print(f"   - Documents: {stats['total_documents']}")
    print(f"   - BM25 Weight: {stats['weight_bm25']}")
    print(f"   - Semantic Weight: {stats['weight_semantic']}")
    
    # Test queries
    queries = [
        "python programming",
        "how to find information fast",
        "building websites with python",
        "analyzing data with statistics",
        "artificial intelligence"
    ]
    
    print("\n🔍 Hybrid Search Results:")
    print("-" * 40)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        results = hybrid.get_top_documents(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (Score: {result['score']})")
        else:
            print("   No results found")
    
    print("\n" + "="*50)
    print("✅ Hybrid search test complete!")
    print("="*50 + "\n")


def test_weight_comparison():
    """Test different weight combinations"""
    
    print("\n" + "="*50)
    print("⚖️ TESTING DIFFERENT WEIGHT COMBINATIONS")
    print("="*50 + "\n")
    
    query = "python programming"
    
    # Test different weight configurations
    configs = [
        (1.0, 0.0, "BM25 Only"),
        (0.0, 1.0, "Semantic Only"),
        (0.7, 0.3, "BM25 Weighted"),
        (0.5, 0.5, "Balanced"),
        (0.3, 0.7, "Semantic Weighted"),
    ]
    
    for bm25_w, sem_w, name in configs:
        print(f"📊 {name} (BM25: {bm25_w}, Semantic: {sem_w})")
        
        hybrid = HybridSearch(weight_bm25=bm25_w, weight_semantic=sem_w)
        
        # Add documents
        docs = [
            ('doc1', 'Python Programming Guide', 'Python is a versatile programming language.'),
            ('doc2', 'Search Engine Basics', 'Search engines use ranking algorithms.'),
            ('doc3', 'Web Development with Python', 'Web development with Python is popular.'),
        ]
        
        for doc_id, title, content in docs:
            hybrid.add_document(doc_id, title, content)
        
        results = hybrid.get_top_documents(query, limit=3)
        
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r['title']} (Score: {r['score']})")
        print()


if __name__ == "__main__":
    test_hybrid_search()
    test_weight_comparison()
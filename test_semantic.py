"""
Test script for semantic search
"""

import logging
from app.retrieval.semantic import SemanticSearch

# Set up logging
logging.basicConfig(level=logging.INFO)


def test_semantic_search():
    """Test semantic search with sample documents"""
    
    print("\n" + "="*50)
    print("🧠 TESTING SEMANTIC SEARCH")
    print("="*50 + "\n")
    
    # Create semantic search index
    semantic = SemanticSearch(model_name="all-MiniLM-L6-v2")
    
    # Sample documents
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming',
            'content': 'Python is a versatile programming language. Python is great for beginners.'
        },
        {
            'id': 'doc2',
            'title': 'Search Engines',
            'content': 'Search engines use algorithms to find relevant documents quickly.'
        },
        {
            'id': 'doc3',
            'title': 'Web Development',
            'content': 'Web development involves building websites and web applications with Python.'
        },
        {
            'id': 'doc4',
            'title': 'Data Science',
            'content': 'Data science uses programming and statistics to find insights in data.'
        },
        {
            'id': 'doc5',
            'title': 'Machine Learning',
            'content': 'Machine learning is a subset of artificial intelligence that uses data to train models.'
        }
    ]
    
    print("📄 Adding documents...\n")
    for doc in documents:
        semantic.add_document(doc['id'], doc['title'], doc['content'])
        print(f"   ✅ Added: {doc['title']}")
    
    stats = semantic.get_stats()
    print(f"\n📊 Semantic Search Stats:")
    print(f"   - Documents: {stats['total_documents']}")
    print(f"   - Embedding dimension: {stats['embedding_dimension']}")
    
    # Test queries
    queries = [
        "programming language",
        "how to find information quickly",
        "building websites",
        "analyzing data with statistics",
        "artificial intelligence"
    ]
    
    print("\n🔍 Semantic Search Results:")
    print("-" * 40)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        results = semantic.get_top_documents(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (Similarity: {result['similarity']})")
        else:
            print("   No results found")
    
    print("\n" + "="*50)
    print("✅ Semantic search test complete!")
    print("="*50 + "\n")


def test_synonyms():
    """Test semantic search with synonyms"""
    
    print("\n" + "="*50)
    print("🔄 TESTING SYNONYM HANDLING")
    print("="*50 + "\n")
    
    semantic = SemanticSearch()
    
    # Add documents
    docs = [
        {'id': 'doc1', 'title': 'Car Guide', 'content': 'Cars are vehicles with four wheels.'},
        {'id': 'doc2', 'title': 'Automobile Safety', 'content': 'Automobiles have advanced safety features.'},
        {'id': 'doc3', 'title': 'Vehicle Maintenance', 'content': 'Vehicles need regular maintenance.'}
    ]
    
    for doc in docs:
        semantic.add_document(doc['id'], doc['title'], doc['content'])
    
    # Search with synonyms
    queries = ["car", "automobile", "vehicle", "auto"]
    
    for query in queries:
        print(f"📝 Query: '{query}'")
        results = semantic.get_top_documents(query, limit=3)
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r['title']} (Similarity: {r['similarity']})")
        print()
    
    print("✅ Note: Semantic search finds related documents even with different words!")


if __name__ == "__main__":
    test_semantic_search()
    test_synonyms()

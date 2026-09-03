"""
Test script for the inverted index
"""

import logging
from app.indexing.inverted_index import InvertedIndex
from app.indexing.tokenizer import Tokenizer

logging.basicConfig(level=logging.INFO)


def test_indexing():
    print("\n" + "="*50)
    print("📚 TESTING INVERTED INDEX")
    print("="*50 + "\n")
    
    index = InvertedIndex()
    
    documents = [
        {'id': 'doc1', 'title': 'Python Programming', 
         'content': 'Python is a great programming language for beginners. Python is versatile.'},
        {'id': 'doc2', 'title': 'Search Engine Basics', 
         'content': 'Search engines use inverted indexes to find documents quickly. Search is fast.'},
        {'id': 'doc3', 'title': 'Web Development', 
         'content': 'Web development involves building websites and web applications with Python.'},
        {'id': 'doc4', 'title': 'Data Science', 
         'content': 'Data science uses programming and statistics to find insights in data.'}
    ]
    
    print("📄 Adding documents to index...\n")
    for doc in documents:
        index.add_document(doc['id'], doc['title'], doc['content'])
        print(f"   ✅ Added: {doc['title']} ({doc['id']})")
    
    stats = index.get_stats()
    print(f"\n📊 Index Statistics:")
    print(f"   - Documents: {stats['total_documents']}")
    print(f"   - Unique terms: {stats['unique_terms']}")
    
    queries = ["python", "search", "programming language", "web development", "data science"]
    
    print("\n🔍 Search Results:")
    print("-" * 40)
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        results = index.get_top_documents(query, limit=3)
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (Score: {result['score']})")
        else:
            print("   No results found")
    
    print("\n" + "="*50)
    print("✅ Inverted index test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_indexing()

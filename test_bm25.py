"""
Test script for BM25 implementation
"""

import logging
from app.indexing.bm25 import BM25

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_bm25():
    """Test BM25 implementation"""
    
    print("\n" + "="*50)
    print("📊 TESTING BM25")
    print("="*50 + "\n")
    
    # Create BM25 with default parameters
    bm25 = BM25(k1=1.2, b=0.75)
    
    # Sample documents (same as TF-IDF test for comparison)
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming',
            'content': 'Python is a great programming language. Python is versatile.'
        },
        {
            'id': 'doc2',
            'title': 'Search Engine Basics',
            'content': 'Search engines use inverted indexes to find documents quickly. Search is fast.'
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
        }
    ]
    
    print("📄 Adding documents to BM25...\n")
    for doc in documents:
        bm25.add_document(doc['id'], doc['title'], doc['content'])
        print(f"   ✅ Added: {doc['title']} ({doc['id']})")
    
    # Display stats
    stats = bm25.get_stats()
    print(f"\n📊 BM25 Statistics:")
    print(f"   - Total documents: {stats['total_documents']}")
    print(f"   - Unique terms: {stats['unique_terms']}")
    print(f"   - Total terms: {stats['total_terms']}")
    print(f"   - Average document length: {stats['avgdl']}")
    print(f"   - Parameters: k1={stats['params']['k1']}, b={stats['params']['b']}")
    
    # Test queries
    queries = [
        "python programming",
        "search engine",
        "web development with python",
        "data science"
    ]
    
    print("\n🔍 Search Results with BM25:")
    print("-" * 40)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        results = bm25.get_top_documents(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} (Score: {result['score']})")
                print(f"      Terms: {result['total_terms']}, Unique: {result['unique_terms']}")
        else:
            print("   No results found")
    
    # Explain a score
    print("\n📖 Score Explanation:")
    print("-" * 40)
    
    query = "python programming"
    doc_id = "doc1"
    
    print(f"\n📝 Query: '{query}'")
    print(f"📄 Document: {doc_id}")
    
    explanation = bm25.explain_score(doc_id, query)
    if 'error' in explanation:
        print(f"   Error: {explanation['error']}")
    else:
        print(f"   Total Score: {explanation['total_score']}")
        print(f"   Document length: {explanation['doc_length']}")
        print(f"   Average document length: {explanation['avgdl']}")
        print(f"   Parameters: k1={explanation['params']['k1']}, b={explanation['params']['b']}")
        print("\n   Breakdown:")
        for item in explanation['breakdown']:
            print(f"   - {item['term']}: TF={item['tf']}, IDF={item['idf']}, Contribution={item['contribution']}")
    
    print("\n" + "="*50)
    print("✅ BM25 test complete!")
    print("="*50 + "\n")


def compare_bm25_vs_tfidf():
    """Compare BM25 with TF-IDF"""
    
    print("\n" + "="*50)
    print("📊 BM25 vs TF-IDF Comparison")
    print("="*50 + "\n")
    
    from app.indexing.tfidf import TFIDF
    
    # Same documents with varying lengths
    docs = [
        {'id': 'doc1', 'title': 'Short Doc', 'content': 'Python is great.'},
        {'id': 'doc2', 'title': 'Long Doc', 'content': 'Python Python Python Python Python Python Python Python Python Python Python Python Python Python Python is great.'},
        {'id': 'doc3', 'title': 'Medium Doc', 'content': 'Python is a great programming language.'}
    ]
    
    query = "python"
    
    print(f"📝 Query: '{query}'")
    print("\n   TF-IDF Scores:")
    
    tfidf = TFIDF()
    for doc in docs:
        tfidf.add_document(doc['id'], doc['title'], doc['content'])
    
    for doc_id, score in tfidf.search(query)[:3]:
        print(f"   - {doc_id}: {score:.4f}")
    
    print("\n   BM25 Scores:")
    
    bm25 = BM25(k1=1.2, b=0.75)
    for doc in docs:
        bm25.add_document(doc['id'], doc['title'], doc['content'])
    
    for doc_id, score in bm25.search(query)[:3]:
        print(f"   - {doc_id}: {score:.4f}")
    
    print("\n   Note: BM25 penalizes the long document more than TF-IDF!")
    print("   This is because BM25 normalizes for document length.")


if __name__ == "__main__":
    test_bm25()
    compare_bm25_vs_tfidf()
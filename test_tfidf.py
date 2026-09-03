"""
Test script for TF-IDF implementation
"""

import logging
from app.indexing.tfidf import TFIDF

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_tfidf():
    """Test TF-IDF implementation"""
    
    print("\n" + "="*50)
    print("📊 TESTING TF-IDF")
    print("="*50 + "\n")
    
    # Create TF-IDF calculator
    tfidf = TFIDF()
    
    # Sample documents
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
    
    print("📄 Adding documents to TF-IDF...\n")
    for doc in documents:
        tfidf.add_document(doc['id'], doc['title'], doc['content'])
        print(f"   ✅ Added: {doc['title']} ({doc['id']})")
    
    # Display stats
    stats = tfidf.get_stats()
    print(f"\n📊 TF-IDF Statistics:")
    print(f"   - Total documents: {stats['total_documents']}")
    print(f"   - Unique terms: {stats['unique_terms']}")
    print(f"   - Total terms: {stats['total_terms']}")
    print(f"   - Average terms per document: {stats['avg_terms_per_doc']:.2f}")
    
    # Test term information
    print("\n📝 Term Information:")
    print("-" * 40)
    for term in ['python', 'programming', 'search', 'data']:
        info = tfidf.get_term_info(term)
        print(f"\n   Term: '{term}'")
        print(f"   - Document frequency: {info['document_frequency']}")
        print(f"   - IDF: {info['idf']}")
        print(f"   - Appears in: {info['appears_in']}")
    
    # Test queries
    queries = [
        "python programming",
        "search engine",
        "web development with python",
        "data science"
    ]
    
    print("\n🔍 Search Results with TF-IDF:")
    print("-" * 40)
    
    for query in queries:
        print(f"\n📝 Query: '{query}'")
        results = tfidf.get_top_documents(query, limit=3)
        
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
    
    explanation = tfidf.explain_score(doc_id, query)
    if 'error' in explanation:
        print(f"   Error: {explanation['error']}")
    else:
        print(f"   Total Score: {explanation['total_score']}")
        print("\n   Breakdown:")
        for item in explanation['breakdown']:
            print(f"   - {item['term']}: TF={item['tf']}, IDF={item['idf']}, TF-IDF={item['tfidf']} (freq: {item['frequency']})")
    
    print("\n" + "="*50)
    print("✅ TF-IDF test complete!")
    print("="*50 + "\n")


def compare_tfidf_vs_bm25():
    """Compare TF-IDF vs simple scoring"""
    
    print("\n" + "="*50)
    print("📊 TF-IDF vs Simple Scoring")
    print("="*50 + "\n")
    
    tfidf = TFIDF()
    
    # Add sample documents
    docs = [
        {'id': 'doc1', 'title': 'Python Guide', 'content': 'Python is a powerful programming language.'},
        {'id': 'doc2', 'title': 'Java Guide', 'content': 'Java is a popular programming language.'},
        {'id': 'doc3', 'title': 'Python vs Java', 'content': 'Python and Java are both programming languages.'}
    ]
    
    for doc in docs:
        tfidf.add_document(doc['id'], doc['title'], doc['content'])
    
    query = "python java"
    print(f"📝 Query: '{query}'")
    print("\n   TF-IDF Scores:")
    
    results = tfidf.search(query)
    for doc_id, score in results[:3]:
        print(f"   - {doc_id}: {score:.4f}")
    
    print("\n   Simple Term Frequency (without IDF):")
    # Simple scoring (just term frequency)
    query_tokens = tfidf.tokenizer.tokenize(query)
    for doc_id, doc in tfidf.documents.items():
        simple_score = sum(doc['term_freq'].get(token, 0) for token in query_tokens)
        print(f"   - {doc_id}: {simple_score}")
    
    print("\n   Notice how TF-IDF penalizes documents with common terms!")


if __name__ == "__main__":
    test_tfidf()
    compare_tfidf_vs_bm25()
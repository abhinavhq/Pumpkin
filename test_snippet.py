"""
Test script for snippet generation
"""

from app.search.snippet import SnippetGenerator


def test_snippet():
    """Test snippet generation"""
    
    print("\n" + "="*50)
    print("📝 TESTING SNIPPET GENERATOR")
    print("="*50 + "\n")
    
    # Create snippet generator
    generator = SnippetGenerator(
        max_snippet_length=200,
        context_window=30,
        max_snippets=3
    )
    
    # Test content
    content = """
    Python is a versatile programming language. Python is great for beginners.
    It has a simple syntax that makes it easy to learn. Python is used in many fields:
    web development, data science, machine learning, and automation.
    The Python programming language was created by Guido van Rossum.
    Python's design philosophy emphasizes code readability.
    """
    
    queries = [
        "python programming",
        "data science",
        "machine learning",
        "web development"
    ]
    
    for query in queries:
        print(f"📝 Query: '{query}'")
        print(f"📄 Content: {content[:100]}...")
        
        snippet = generator.generate(content, query)
        print(f"\n📊 Snippet:")
        print(f"   {snippet}")
        print("-" * 40)
        print()


def test_with_database():
    """Test snippet generation with real database documents"""
    
    print("\n" + "="*50)
    print("📝 TESTING SNIPPET WITH DATABASE")
    print("="*50 + "\n")
    
    from app.database.database import Database
    from app.database.repositories import DocumentRepository
    
    db = Database("data/search.db")
    repo = DocumentRepository(db)
    
    documents = repo.get_all(limit=5)
    
    if not documents:
        print("No documents in database. Run seed_simple.py first.")
        return
    
    generator = SnippetGenerator()
    queries = ["python", "search", "data", "web"]
    
    for query in queries:
        print(f"📝 Query: '{query}'")
        print("-" * 30)
        
        for doc in documents[:2]:
            snippet = generator.generate(doc.content or "", query)
            print(f"\n📄 {doc.title}")
            print(f"   {snippet}")
        
        print()


if __name__ == "__main__":
    test_snippet()
    # Uncomment to test with database:
    test_with_database()

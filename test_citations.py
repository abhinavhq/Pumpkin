"""
Test script for citation system
"""

import asyncio
import logging
from app.ai.rag import RAGEngine
from app.ai.provider import MockAIProvider
from app.ai.citations import CitationSystem

logging.basicConfig(level=logging.INFO)


async def test_citations():
    """Test citation system"""
    
    print("\n" + "="*50)
    print("📚 TESTING CITATION SYSTEM")
    print("="*50 + "\n")
    
    # Test citation system
    citation_system = CitationSystem()
    
    # Sample answer and sources
    answer = """Python is a versatile programming language created by Guido van Rossum. 
    Python emphasizes code readability and simplicity. 
    It is widely used in data science, web development, and automation. 
    Python has a large community and extensive libraries."""
    
    sources = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide',
            'url': 'https://python.org/guide',
            'content': 'Python is a versatile programming language created by Guido van Rossum. Python emphasizes code readability and simplicity.'
        },
        {
            'id': 'doc2',
            'title': 'Python for Data Science',
            'url': 'https://python.org/datascience',
            'content': 'Python is widely used in data science and machine learning. It has powerful libraries like NumPy and Pandas.'
        },
        {
            'id': 'doc3',
            'title': 'Python Web Development',
            'url': 'https://python.org/web',
            'content': 'Python is used in web development with frameworks like Django and Flask.'
        }
    ]
    
    print("📄 Original Answer:")
    print(answer)
    print("\n" + "-" * 40)
    
    # Add citations
    result = citation_system.add_citations(answer, sources)
    
    print("\n📄 Answer with Citations:")
    print(result['text'])
    
    print("\n📚 Citations:")
    for citation in result['citations']:
        verified = "✅" if citation.get('verified') else "❌"
        print(f"   [{citation['id']}] {verified} {citation['title']}")
        print(f"      🔗 {citation['url']}")
        print(f"      📝 {citation['snippet'][:100]}...")
    
    print(f"\n📊 Citation Count: {result['citation_count']}")
    
    print("\n" + "="*50)
    print("✅ Citation system test complete!")
    print("="*50 + "\n")


async def test_rag_with_citations():
    """Test full RAG pipeline with citations"""
    
    print("\n" + "="*50)
    print("🤖 TESTING RAG WITH CITATIONS")
    print("="*50 + "\n")
    
    rag = RAGEngine(provider=MockAIProvider())
    
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide',
            'url': 'https://python.org/guide',
            'content': 'Python is a versatile programming language created by Guido van Rossum. It emphasizes code readability and simplicity.'
        },
        {
            'id': 'doc2',
            'title': 'Python for Data Science',
            'url': 'https://python.org/datascience',
            'content': 'Python is widely used in data science and machine learning. It has powerful libraries like NumPy and Pandas.'
        },
        {
            'id': 'doc3',
            'title': 'Python Web Development',
            'url': 'https://python.org/web',
            'content': 'Python is used in web development with frameworks like Django and Flask.'
        }
    ]
    
    query = "What is Python and what is it used for?"
    
    print(f"📝 Query: '{query}'")
    print("-" * 40)
    
    result = await rag.generate(query, documents, include_citations=True)
    
    print(f"\n📄 Answer with Citations:")
    print(result['answer'])
    
    print(f"\n📚 Citations:")
    for citation in result.get('citations', []):
        print(f"   [{citation['id']}] {citation['title']}")
        print(f"      🔗 {citation['url']}")
    
    print(f"\n📊 Citation Count: {result.get('citation_count', 0)}")
    
    print("\n" + "="*50)
    print("✅ RAG with citations test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(test_citations())
    asyncio.run(test_rag_with_citations())
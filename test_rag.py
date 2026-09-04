"""
Test script for RAG (Retrieval-Augmented Generation)
"""

import asyncio
import logging
from app.ai.rag import RAGEngine
from app.ai.provider import MockAIProvider

logging.basicConfig(level=logging.INFO)


async def test_rag():
    print("\n" + "="*50)
    print("🤖 TESTING RAG PIPELINE")
    print("="*50 + "\n")
    
    engine = RAGEngine(provider=MockAIProvider())
    
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide',
            'url': 'https://python.org/guide',
            'content': 'Python is a versatile programming language created by Guido van Rossum.',
        },
        {
            'id': 'doc2',
            'title': 'Python for Beginners',
            'url': 'https://python.org/beginners',
            'content': 'Python is great for beginners because of its simple syntax.',
        },
        {
            'id': 'doc3',
            'title': 'Data Science with Python',
            'url': 'https://python.org/datascience',
            'content': 'Python is the leading language for data science.',
        }
    ]
    
    queries = ["What is Python?", "Why is Python good for beginners?"]
    
    for query in queries:
        print(f"📝 Query: '{query}'")
        print("-" * 40)
        
        result = await engine.generate(query, documents)
        
        print(f"\n📄 Answer:")
        print(f"{result['answer']}")
        
        if result['citations']:
            print(f"\n📚 Citations:")
            for citation in result['citations']:
                print(f"   [{citation['id']}] {citation['title']}")
        
        print("\n" + "="*40 + "\n")


async def main():
    await test_rag()


if __name__ == "__main__":
    asyncio.run(main())

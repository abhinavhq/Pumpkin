"""
Test script for grounded answers
"""

import asyncio
import logging
from app.ai.rag import RAGEngine
from app.ai.provider import MockAIProvider
from app.ai.grounded import GroundedAnswer

logging.basicConfig(level=logging.INFO)


async def test_grounded_answers():
    """Test grounded answer generation"""
    
    print("\n" + "="*50)
    print("✅ TESTING GROUNDED ANSWERS")
    print("="*50 + "\n")
    
    rag = RAGEngine(provider=MockAIProvider())
    grounded = GroundedAnswer(confidence_threshold=0.4)
    
    documents = [
        {
            'id': 'doc1',
            'title': 'Python Programming Guide',
            'url': 'https://python.org/guide',
            'content': 'Python is a versatile programming language created by Guido van Rossum. Python emphasizes code readability and simplicity.',
        },
        {
            'id': 'doc2',
            'title': 'Python for Data Science',
            'url': 'https://python.org/datascience',
            'content': 'Python is widely used in data science and machine learning. It has powerful libraries like NumPy and Pandas.',
        }
    ]
    
    query = "What is Python and what is it used for?"
    
    print(f"📝 Query: '{query}'")
    print("-" * 40)
    
    result = await rag.generate(query, documents)
    raw_answer = result['answer']
    
    print(f"\n📄 Raw Answer:")
    print(raw_answer)
    
    grounded_result = grounded.process(
        answer=raw_answer,
        sources=documents,
        query=query
    )
    
    print(f"\n📊 Grounded Answer:")
    print(grounded_result['answer'])
    
    print(f"\n📊 Verification Stats:")
    print(f"   Confidence: {grounded_result['confidence']:.2%}")
    print(f"   Total Facts: {grounded_result['total_facts']}")
    print(f"   Sources Used: {grounded_result['sources_used']}")
    
    print("\n" + "="*50)
    print("✅ Grounded answers test complete!")
    print("="*50 + "\n")


async def test_insufficient_evidence():
    """Test when there's not enough evidence"""
    
    print("\n" + "="*50)
    print("⚠️ TESTING INSUFFICIENT EVIDENCE")
    print("="*50 + "\n")
    
    rag = RAGEngine(provider=MockAIProvider())
    grounded = GroundedAnswer(confidence_threshold=0.5)
    
    documents = []
    query = "What is the capital of France?"
    
    print(f"📝 Query: '{query}'")
    print("-" * 40)
    
    result = await rag.generate(query, documents)
    raw_answer = result['answer']
    
    print(f"\n📄 Raw Answer:")
    print(raw_answer)
    
    grounded_result = grounded.process(
        answer=raw_answer,
        sources=documents,
        query=query
    )
    
    print(f"\n📊 Grounded Answer:")
    print(grounded_result['answer'])
    
    print("\n" + "="*50)
    print("✅ Test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(test_grounded_answers())
    asyncio.run(test_insufficient_evidence())

"""
Test script for search modes
"""

import asyncio
import logging
from app.search.modes import SearchModes, SearchMode
from app.retrieval.hybrid import HybridSearch
from app.ai.rag import RAGEngine
from app.ai.provider import MockAIProvider

logging.basicConfig(level=logging.INFO)


async def test_search_modes():
    """Test all search modes"""
    
    print("\n" + "="*50)
    print("🔍 TESTING SEARCH MODES")
    print("="*50 + "\n")
    
    hybrid = HybridSearch(weight_bm25=0.5, weight_semantic=0.5)
    rag = RAGEngine(provider=MockAIProvider())
    
    docs = [
        {'id': 'doc1', 'title': 'Python Programming Guide', 
         'content': 'Python is a versatile programming language.'},
        {'id': 'doc2', 'title': 'Data Science with Python', 
         'content': 'Python is used for data science and machine learning.'},
        {'id': 'doc3', 'title': 'Web Development with Python', 
         'content': 'Python is used for web development with Django and Flask.'},
    ]
    
    for doc in docs:
        hybrid.add_document(doc['id'], doc['title'], doc['content'])
    
    modes = SearchModes()
    modes.init_engines(hybrid, rag)
    
    query = "What is Python used for?"
    
    modes_to_test = [
        (SearchMode.WEB, "Web Search"),
        (SearchMode.AI, "AI Search"),
        (SearchMode.RESEARCH, "Research Mode"),
        (SearchMode.DEEP, "Deep Search"),
    ]
    
    for mode, name in modes_to_test:
        print(f"\n📋 {name} ({mode.value})")
        print("-" * 40)
        
        result = await modes.search(query, mode, limit=5)
        
        print(f"   Query: {result.get('query', '')}")
        print(f"   Mode: {result.get('mode', '')}")
        print(f"   Type: {result.get('type', '')}")
        print(f"   Total Results: {result.get('total', 0)}")
        
        if mode == SearchMode.WEB:
            results = result.get('results', [])
            print(f"   Results: {len(results)} documents found")
            for r in results[:2]:
                print(f"      - {r.get('title', '')} (Score: {r.get('score', 0):.4f})")
        
        elif mode == SearchMode.AI:
            answer = result.get('answer', '')[:150]
            print(f"   AI Answer: {answer}...")
            print(f"   Citations: {len(result.get('citations', []))}")
        
        elif mode == SearchMode.RESEARCH:
            print(f"   Topics: {list(result.get('topics', {}).keys())}")
        
        elif mode == SearchMode.DEEP:
            print(f"   Follow-ups: {result.get('follow_up_questions', [])}")
    
    print("\n" + "="*50)
    print("✅ Search modes test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(test_search_modes())

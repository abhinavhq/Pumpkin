"""
Test script for query understanding
"""

import logging
from app.query.processor import QueryProcessor

logging.basicConfig(level=logging.INFO)


def test_spelling_correction():
    print("\n" + "="*50)
    print("✏️ TESTING SPELLING CORRECTION")
    print("="*50 + "\n")
    
    processor = QueryProcessor()
    
    misspelled = [
        ("pythn", "python"),
        ("programing", "programming"),
        ("datascience", "data science"),
        ("machinelearning", "machine learning"),
        ("begginer", "beginner"),
        ("tutoral", "tutorial"),
    ]
    
    for wrong, correct in misspelled:
        result = processor.correct_spelling(wrong)
        status = "✅" if result == correct else "❌"
        print(f"   {status} '{wrong}' → '{result}' (Expected: '{correct}')")


def test_intent_detection():
    print("\n" + "="*50)
    print("🎯 TESTING INTENT DETECTION")
    print("="*50 + "\n")
    
    processor = QueryProcessor()
    
    queries = [
        ("how to learn python", "informational"),
        ("buy python course", "transactional"),
        ("python.org official website", "navigational"),
        ("django vs flask", "comparison"),
        ("what is machine learning", "informational"),
    ]
    
    for query, expected in queries:
        intent = processor.detect_intent(query)
        status = "✅" if intent == expected else "❌"
        print(f"   {status} '{query}' → {intent} (Expected: {expected})")


def test_query_processor():
    print("\n" + "="*50)
    print("🧠 TESTING QUERY UNDERSTANDING")
    print("="*50 + "\n")
    
    processor = QueryProcessor()
    
    test_queries = [
        "pythn programing",
        "how to learn pythn for datascience",
        "best java script framework",
        "what is machine learning",
        "django vs flask",
    ]
    
    for query in test_queries:
        print(f"📝 Original: '{query}'")
        result = processor.process(query)
        print(f"   ✅ Corrected: '{result['corrected']}'")
        print(f"   📚 Expanded: {result['expanded'][:5]}...")
        print(f"   🎯 Intent: {result['intent']}")
        print(f"   🔍 Entities: {result['entities']}")
        print("-" * 40)


if __name__ == "__main__":
    test_spelling_correction()
    test_intent_detection()
    test_query_processor()

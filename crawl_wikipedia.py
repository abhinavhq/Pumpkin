"""
Crawl Wikipedia and save to database - WORKING VERSION
"""

import requests
import time
from app.database.database import Database
from app.database.models import Document
from app.database.repositories import DocumentRepository
from app.parser.simple_parser import SimpleParser

# Initialize
db = Database("data/search.db")
repo = DocumentRepository(db)
parser = SimpleParser()

# Wikipedia URLs to crawl
urls = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://en.wikipedia.org/wiki/Machine_learning",
    "https://en.wikipedia.org/wiki/Data_science",
    "https://en.wikipedia.org/wiki/Cloud_computing",
    "https://en.wikipedia.org/wiki/Cybersecurity",
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://en.wikipedia.org/wiki/JavaScript",
    "https://en.wikipedia.org/wiki/Java_(programming_language)",
    "https://en.wikipedia.org/wiki/SQL",
    "https://en.wikipedia.org/wiki/React_(JavaScript_library)",
    "https://en.wikipedia.org/wiki/Quantum_computing",
    "https://en.wikipedia.org/wiki/Blockchain",
    "https://en.wikipedia.org/wiki/Internet_of_things",
    "https://en.wikipedia.org/wiki/Augmented_reality",
    "https://en.wikipedia.org/wiki/Virtual_reality",
    "https://en.wikipedia.org/wiki/Google",
    "https://en.wikipedia.org/wiki/Microsoft",
    "https://en.wikipedia.org/wiki/Amazon_(company)",
    "https://en.wikipedia.org/wiki/Apple_Inc.",
    "https://en.wikipedia.org/wiki/Tesla,_Inc.",
]

print("="*60)
print("🌐 CRAWLING WIKIPEDIA")
print("="*60 + "\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

saved_count = 0

for url in urls:
    try:
        print(f"📡 Fetching: {url}")
        
        # Get the page
        response = requests.get(url, headers=headers)
        html = response.text
        
        # Parse with SimpleParser
        parsed = parser.parse(html)
        
        title = parsed['title']
        content = parsed['content']
        word_count = parsed['word_count']
        
        if word_count > 50:
            # Save to database
            doc = Document(
                url=url,
                title=title,
                content=content,
                description='',
                headings={},
                keywords=[],
                word_count=word_count
            )
            
            doc_id = repo.save(doc)
            saved_count += 1
            print(f"  ✅ Saved: {title[:50]}... ({word_count} words)")
        else:
            print(f"  ⚠️ Not enough content: {word_count} words")
        
        # Be respectful
        time.sleep(0.5)
        
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Show stats
stats = db.get_stats()
print(f"\n📊 Database Stats:")
print(f"   - Total Documents: {stats['documents']}")
print(f"   - Total Words: {stats['total_words']}")
print(f"   - Saved this run: {saved_count}")

print("\n" + "="*60)
print("✅ Crawl complete!")
print("="*60 + "\n")
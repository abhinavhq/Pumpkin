"""
Crawl real websites and save to database
"""

import asyncio
import sys
import logging
from app.crawler.crawler import Crawler
from app.database.database import Database
from app.database.models import Document
from app.database.repositories import DocumentRepository
from app.parser.wikipedia_parser import WikipediaParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def crawl_and_save():
    """Crawl websites and save to database"""
    
    print("\n" + "="*60)
    print("🌐 CRAWLING REAL WEBSITES")
    print("="*60 + "\n")
    
    db = Database("data/search.db")
    repo = DocumentRepository(db)
    parser = WikipediaParser()
    
    crawler = Crawler(
        max_pages=20,
        max_depth=1,
        delay=1.0,
        timeout=20,
        user_agent="Mozilla/5.0 (compatible; PumpkinBot/1.0)"
    )
    
    seed_urls = [
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
    
    print(f"📡 Starting crawl with {len(seed_urls)} seed URLs...")
    print(f"   Max pages: {crawler.max_pages}")
    print("   Please wait, this may take a few minutes...\n")
    
    results = await crawler.crawl(seed_urls)
    
    print(f"\n✅ Crawled {len(results)} pages")
    print("-" * 40)
    
    saved_count = 0
    for page in results:
        try:
            url = page.get('url', '')
            html = page.get('content', '')
            
            if not html:
                print(f"  ⚠️ No HTML for {url}")
                continue
            
            # Parse the HTML using Wikipedia parser
            parsed = parser.parse(html)
            
            # Get the content and word count
            content = parsed.get('content', '')
            word_count = parsed.get('word_count', 0)
            title = parsed.get('title', 'No Title')
            
            if word_count == 0:
                print(f"  ⚠️ No content extracted from {title[:30]}")
                continue
            
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
            
            print(f"  ✅ {doc.title[:50]}... ({doc.word_count} words)")
            
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:100]}")
    
    stats = db.get_stats()
    print(f"\n📊 Database Stats:")
    print(f"   - Total Documents: {stats['documents']}")
    print(f"   - Total Words: {stats['total_words']}")
    
    await crawler.close()
    
    print("\n" + "="*60)
    print("✅ Crawl complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(crawl_and_save())
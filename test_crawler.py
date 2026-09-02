"""
Test script for the web crawler
"""

import asyncio
import logging
from app.crawler.crawler import Crawler

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_crawler():
    """Test the crawler with a simple website"""
    
    print("\n" + "="*50)
    print("🚀 TESTING WEB CRAWLER")
    print("="*50 + "\n")
    
    # Create crawler with small limits
    crawler = Crawler(
        max_pages=3,        # Crawl only 3 pages
        max_depth=1,        # Only top level
        delay=2.0,          # Be respectful (2 seconds between requests)
        timeout=15,         # 15 second timeout
        user_agent="AISearchBot/1.0"
    )
    
    # Start crawling with seed URLs
    seed_urls = [
        "https://example.com",
        # "https://httpbin.org/html",  # Uncomment for more test pages
    ]
    
    print(f"🌱 Starting crawl with {len(seed_urls)} seed URLs...\n")
    
    try:
        results = await crawler.crawl(seed_urls)
        
        print(f"\n✅ Crawling complete!")
        print(f"📊 Results Summary:")
        print(f"   - Pages crawled: {len(results)}")
        print(f"   - Failed pages: {crawler.failed_pages}")
        
        print("\n📄 Page Details:")
        for i, page in enumerate(results, 1):
            print(f"\n   [{i}] {page['url']}")
            print(f"       Title: {page['title']}")
            print(f"       Links found: {page['links_count']}")
            print(f"       Content size: {page['content_size']} bytes")
        
    except Exception as e:
        print(f"\n❌ Error during crawl: {e}")
    
    finally:
        await crawler.close()
        print("\n🔒 Crawler closed")


if __name__ == "__main__":
    asyncio.run(test_crawler())
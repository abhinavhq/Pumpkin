"""
Debug crawler output
"""

import asyncio
from app.crawler.crawler import Crawler


async def debug_crawl():
    crawler = Crawler(max_pages=1, max_depth=1, delay=0)
    
    # Test with a single URL
    url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    results = await crawler.crawl([url])
    
    print(f"Results length: {len(results)}")
    
    if results:
        page = results[0]
        print(f"Keys: {page.keys()}")
        print(f"URL: {page.get('url', 'No URL')}")
        print(f"Title: {page.get('title', 'No Title')}")
        print(f"Content length: {len(page.get('content', ''))}")
        print(f"Content preview: {page.get('content', '')[:200]}")
    
    await crawler.close()

if __name__ == "__main__":
    asyncio.run(debug_crawl())
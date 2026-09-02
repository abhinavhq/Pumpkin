"""
Test script for the HTML parser
"""

import logging
from app.parser.html_parser import HTMLParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def test_parser():
    """Test the HTML parser with sample HTML"""
    
    print("\n" + "="*50)
    print("🧹 TESTING HTML PARSER")
    print("="*50 + "\n")
    
    # Sample HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Test Page - Example</title>
        <meta name="description" content="This is a test page for our HTML parser">
        <meta name="keywords" content="test, parser, html, example">
        <style>
            body { color: red; }
            .hidden { display: none; }
        </style>
        <script>
            alert("This should be removed!");
        </script>
    </head>
    <body>
        <header>
            <nav>
                <a href="/home">Home</a>
                <a href="/about">About</a>
            </nav>
        </header>
        
        <main>
            <article>
                <h1>Welcome to My Website</h1>
                <p>This is the first paragraph of content. It contains some important information.</p>
                <p>This is the second paragraph with more details about the topic.</p>
                
                <h2>Section 1: Introduction</h2>
                <p>Introduction paragraph with some text.</p>
                
                <h3>Subsection 1.1</h3>
                <p>Detailed content in the subsection.</p>
                
                <h2>Section 2: Main Content</h2>
                <p>More content here with additional details.</p>
                
                <ul>
                    <li>List item 1</li>
                    <li>List item 2</li>
                    <li>List item 3</li>
                </ul>
                
                <a href="https://example.com/page1">Link 1</a>
                <a href="https://example.com/page2">Link 2</a>
                <a href="https://example.com/page3" rel="nofollow">Link 3</a>
                
                <img src="image1.jpg" alt="Image 1 description">
                <img src="image2.jpg" alt="Image 2 description">
            </article>
        </main>
        
        <footer>
            <p>&copy; 2024 My Website</p>
        </footer>
    </body>
    </html>
    """
    
    # Create parser
    parser = HTMLParser()
    
    print("📄 Parsing HTML...\n")
    
    # Parse the HTML
    result = parser.parse(html, "https://example.com/test")
    
    # Display results
    print("📊 Results:")
    print(f"   Title: {result['title']}")
    print(f"   Description: {result['description']}")
    print(f"   Keywords: {result['keywords']}")
    print(f"   Word Count: {result['word_count']}")
    print(f"   Has Content: {result['has_content']}")
    
    print("\n📑 Headings:")
    for level, headings in result['headings'].items():
        if headings:
            print(f"   {level.upper()}: {headings}")
    
    print("\n📝 Paragraphs:")
    for i, para in enumerate(result['paragraphs'][:5], 1):
        preview = para[:80] + "..." if len(para) > 80 else para
        print(f"   {i}. {preview}")
    
    print(f"\n🔗 Links: {len(result['links'])}")
    for link in result['links'][:5]:
        print(f"   - {link['url']} ({link['text']})")
    
    print(f"\n🖼️ Images: {len(result['images'])}")
    for img in result['images'][:3]:
        print(f"   - {img['src']} (alt: {img['alt']})")
    
    print("\n" + "="*50)
    print("✅ Parser test complete!")
    print("="*50 + "\n")


def test_cleaner():
    """Test just the cleaner functionality"""
    
    print("\n" + "="*50)
    print("🧹 TESTING HTML CLEANER")
    print("="*50 + "\n")
    
    from app.parser.cleaner import HTMLCleaner
    
    cleaner = HTMLCleaner()
    
    html_with_junk = """
    <html>
        <head>
            <script>alert('remove me');</script>
            <style>.hidden { display: none; }</style>
        </head>
        <body>
            <div class="content" style="color: red;">
                <h1>Clean Text</h1>
                <p>This is the content we want to keep.</p>
                <script>console.log('remove this too');</script>
                <p>This is more content.</p>
                <div onclick="alert('remove me')">Click me</div>
            </div>
        </body>
    </html>
    """
    
    print("📄 Cleaning HTML...\n")
    
    clean_text = cleaner.clean(html_with_junk)
    
    print("📊 Clean Text:")
    print("-" * 40)
    print(clean_text)
    print("-" * 40)
    
    print("\n✅ Cleaner test complete!")


if __name__ == "__main__":
    # Run both tests
    test_parser()
    test_cleaner()
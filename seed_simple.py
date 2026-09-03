"""
Simple script to seed documents
"""

import sys
import logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

print("Starting seeding...")

from app.database.database import Database
from app.database.models import Document
from app.database.repositories import DocumentRepository

# Initialize database
print("Initializing database...")
db = Database("data/search.db")
repo = DocumentRepository(db)

# Sample documents
documents = [
    Document(
        url="https://example.com/python-guide",
        title="Python Programming Guide",
        content="Python is a versatile programming language. Python is great for beginners. Learn Python today!",
        description="A comprehensive guide to Python programming",
        headings={"h1": ["Python Guide"], "h2": ["Getting Started", "Advanced Topics"]},
        keywords=["python", "programming", "guide", "tutorial"],
        word_count=30
    ),
    Document(
        url="https://example.com/search-engine",
        title="How Search Engines Work",
        content="Search engines use inverted indexes and ranking algorithms to find relevant documents quickly.",
        description="Understanding search engine internals",
        headings={"h1": ["Search Engine Basics"], "h2": ["Indexing", "Ranking"]},
        keywords=["search", "engine", "index", "ranking"],
        word_count=25
    ),
    Document(
        url="https://example.com/web-dev",
        title="Web Development with Python",
        content="Build web applications with Python using Django and Flask. Python is a popular choice for web development.",
        description="Python web development guide",
        headings={"h1": ["Web Development"], "h2": ["Django", "Flask"]},
        keywords=["web", "development", "python", "django", "flask"],
        word_count=28
    ),
    Document(
        url="https://example.com/data-science",
        title="Data Science with Python",
        content="Data science involves programming, statistics, and machine learning. Python is the go-to language for data science.",
        description="Python data science guide",
        headings={"h1": ["Data Science"], "h2": ["Statistics", "Machine Learning"]},
        keywords=["data", "science", "python", "statistics", "machine learning"],
        word_count=26
    )
]

print(f"Adding {len(documents)} documents...")

for doc in documents:
    doc_id = repo.save(doc)
    print(f"  Added: {doc.title} (ID: {doc_id})")

stats = db.get_stats()
print(f"\nDatabase Stats:")
print(f"  - Documents: {stats['documents']}")
print(f"  - Total words: {stats['total_words']}")

print("\n✅ Seeding complete!")
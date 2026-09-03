"""
Repositories - Data access layer for database operations
"""

import json
import logging
from typing import Optional, List, Dict

from .database import Database
from .models import Document, Link

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository for document operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def save(self, document: Document) -> int:
        """Save a document to the database"""
        existing = self.get_by_url(document.url)
        
        # Convert headings and keywords to JSON strings
        headings_json = json.dumps(document.headings) if document.headings else '{}'
        keywords_json = json.dumps(document.keywords) if document.keywords else '[]'
        
        if existing:
            query = """
                UPDATE documents 
                SET title = ?, content = ?, description = ?, 
                    headings = ?, keywords = ?, word_count = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE url = ?
            """
            params = (
                document.title,
                document.content,
                document.description,
                headings_json,
                keywords_json,
                document.word_count,
                document.url
            )
            self.db.execute_update(query, params)
            return existing.id
        else:
            query = """
                INSERT INTO documents 
                (url, title, content, description, headings, keywords, word_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                document.url,
                document.title,
                document.content,
                document.description,
                headings_json,
                keywords_json,
                document.word_count
            )
            return self.db.execute_insert(query, params)
    
    def get_by_id(self, doc_id: int) -> Optional[Document]:
        query = "SELECT * FROM documents WHERE id = ?"
        result = self.db.execute_query(query, (doc_id,))
        if result:
            return self._row_to_document(dict(result[0]))
        return None
    
    def get_by_url(self, url: str) -> Optional[Document]:
        query = "SELECT * FROM documents WHERE url = ?"
        result = self.db.execute_query(query, (url,))
        if result:
            return self._row_to_document(dict(result[0]))
        return None
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Document]:
        query = "SELECT * FROM documents ORDER BY id LIMIT ? OFFSET ?"
        results = self.db.execute_query(query, (limit, offset))
        docs = []
        for row in results:
            doc = self._row_to_document(dict(row))
            if doc:
                docs.append(doc)
        return docs
    
    def search(self, query_str: str, limit: int = 20) -> List[Document]:
        query = """
            SELECT * FROM documents 
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY word_count DESC
            LIMIT ?
        """
        search_term = f"%{query_str}%"
        results = self.db.execute_query(query, (search_term, search_term, limit))
        docs = []
        for row in results:
            doc = self._row_to_document(dict(row))
            if doc:
                docs.append(doc)
        return docs
    
    def _row_to_document(self, row: dict) -> Optional[Document]:
        """Convert a database row to a Document object"""
        try:
            # Get headings - it's a JSON string from SQLite
            headings_data = row.get('headings', '{}')
            if isinstance(headings_data, str):
                headings = json.loads(headings_data) if headings_data else {}
            elif isinstance(headings_data, dict):
                headings = headings_data
            else:
                headings = {}
            
            # Get keywords - it's a JSON string from SQLite
            keywords_data = row.get('keywords', '[]')
            if isinstance(keywords_data, str):
                keywords = json.loads(keywords_data) if keywords_data else []
            elif isinstance(keywords_data, list):
                keywords = keywords_data
            else:
                keywords = []
            
            # Create and return document
            return Document(
                id=row.get('id'),
                url=row.get('url', ''),
                title=row.get('title', ''),
                content=row.get('content', ''),
                description=row.get('description', ''),
                headings=headings,
                keywords=keywords,
                word_count=row.get('word_count', 0),
                created_at=row.get('created_at'),
                updated_at=row.get('updated_at')
            )
        except Exception as e:
            logger.error(f"Error converting row to document: {e}")
            return None
    
    def get_count(self) -> int:
        query = "SELECT COUNT(*) FROM documents"
        result = self.db.execute_query(query)
        return result[0][0] if result else 0
    
    def delete(self, doc_id: int) -> bool:
        query = "DELETE FROM documents WHERE id = ?"
        rows_affected = self.db.execute_delete(query, (doc_id,))
        return rows_affected > 0


class LinkRepository:
    """Repository for link operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def save(self, link: Link) -> int:
        query = """
            INSERT INTO links (from_url, to_url, text)
            VALUES (?, ?, ?)
        """
        params = (link.from_url, link.to_url, link.text)
        return self.db.execute_insert(query, params)
    
    def get_links_from(self, url: str) -> List[Link]:
        query = "SELECT * FROM links WHERE from_url = ?"
        results = self.db.execute_query(query, (url,))
        return [Link(**dict(row)) for row in results]
    
    def get_count(self) -> int:
        query = "SELECT COUNT(*) FROM links"
        result = self.db.execute_query(query)
        return result[0][0] if result else 0
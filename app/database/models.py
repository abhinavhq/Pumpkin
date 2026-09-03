"""
Database Models - Define table structures
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict
import json


@dataclass
class Document:
    """Document model representing a crawled page"""
    id: Optional[int] = None
    url: str = ""
    title: str = ""
    content: str = ""
    description: str = ""
    headings: Dict = None
    keywords: List[str] = None
    word_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.headings is None:
            self.headings = {}
        if self.keywords is None:
            self.keywords = []
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'content': self.content,
            'description': self.description,
            'headings': json.dumps(self.headings) if self.headings else '{}',
            'keywords': json.dumps(self.keywords) if self.keywords else '[]',
            'word_count': self.word_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        return cls(
            id=data.get('id'),
            url=data.get('url', ''),
            title=data.get('title', ''),
            content=data.get('content', ''),
            description=data.get('description', ''),
            headings=json.loads(data.get('headings', '{}')),
            keywords=json.loads(data.get('keywords', '[]')),
            word_count=data.get('word_count', 0),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )


@dataclass
class Link:
    id: Optional[int] = None
    from_url: str = ""
    to_url: str = ""
    text: str = ""
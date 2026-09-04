"""
AI Provider - Abstract interface for LLM providers
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_answer(
        self,
        query: str,
        context: List[Dict],
        system_prompt: Optional[str] = None
    ) -> Dict:
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        pass


class MockAIProvider(AIProvider):
    """Mock AI provider for testing"""
    
    def __init__(self):
        logger.info("MockAIProvider initialized")
    
    async def generate_answer(
        self,
        query: str,
        context: List[Dict],
        system_prompt: Optional[str] = None
    ) -> Dict:
        if not context:
            return {
                'answer': "No information found.",
                'citations': [],
                'tokens_used': 0
            }
        
        answer = f"Based on {len(context)} documents:\n\n"
        for i, doc in enumerate(context[:3], 1):
            title = doc.get('title', 'Document')
            content = doc.get('content', '')[:200]
            answer += f"[{i}] {title}: {content}...\n\n"
        
        citations = [
            {'id': i, 'title': doc.get('title', 'Unknown'), 'url': doc.get('url', '')}
            for i, doc in enumerate(context[:3], 1)
        ]
        
        return {
            'answer': answer,
            'citations': citations,
            'tokens_used': len(answer.split())
        }
    
    async def is_available(self) -> bool:
        return True

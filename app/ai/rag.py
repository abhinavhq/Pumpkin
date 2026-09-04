"""
RAG - Retrieval-Augmented Generation pipeline
"""

import logging
from typing import List, Dict, Optional

from .provider import AIProvider, MockAIProvider

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine that combines search results with LLM generation"""
    
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or MockAIProvider()
        logger.info("RAGEngine initialized")
    
    async def generate(
        self,
        query: str,
        documents: List[Dict],
        max_documents: int = 3
    ) -> Dict:
        if not documents:
            return {
                'answer': "No relevant documents found.",
                'citations': [],
                'tokens_used': 0
            }
        
        context = documents[:max_documents]
        
        try:
            result = await self.provider.generate_answer(
                query=query,
                context=context
            )
            return result
        except Exception as e:
            logger.error(f"RAG generation failed: {e}")
            return {
                'answer': f"Error: {str(e)}",
                'citations': [],
                'tokens_used': 0
            }
    
    async def is_available(self) -> bool:
        return await self.provider.is_available()

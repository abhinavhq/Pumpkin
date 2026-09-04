"""
RAG - Retrieval-Augmented Generation with Citations
"""

import logging
from typing import List, Dict, Optional

from .provider import AIProvider, MockAIProvider
from .citations import CitationSystem

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG engine that combines search results with LLM generation"""
    
    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or MockAIProvider()
        self.citation_system = CitationSystem()
        logger.info("RAGEngine initialized")
    
    async def generate(
        self,
        query: str,
        documents: List[Dict],
        max_documents: int = 3,
        include_citations: bool = True
    ) -> Dict:
        """
        Generate an AI answer with citations
        """
        if not documents:
            return {
                'answer': "No relevant documents found. Try refining your search.",
                'citations': [],
                'citation_count': 0,
                'tokens_used': 0
            }
        
        context = documents[:max_documents]
        
        try:
            result = await self.provider.generate_answer(
                query=query,
                context=context
            )
            
            # Add citations if enabled
            if include_citations and result.get('answer'):
                citation_result = self.citation_system.add_citations(
                    answer=result['answer'],
                    sources=context
                )
                
                return {
                    'answer': citation_result['text'],
                    'citations': citation_result['citations'],
                    'citation_count': citation_result['citation_count'],
                    'tokens_used': result.get('tokens_used', 0)
                }
            
            return result
            
        except Exception as e:
            logger.error(f"RAG generation failed: {e}")
            return {
                'answer': f"Error generating AI answer: {str(e)}",
                'citations': [],
                'citation_count': 0,
                'tokens_used': 0
            }
    
    async def is_available(self) -> bool:
        return await self.provider.is_available()
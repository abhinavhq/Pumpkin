"""
Search Modes - Different search modes for different use cases
"""

import logging
import asyncio
from typing import List, Dict, Optional
from enum import Enum

from app.indexing.bm25 import BM25
from app.retrieval.hybrid import HybridSearch
from app.ai.rag import RAGEngine
from app.ai.provider import MockAIProvider
from app.ai.citations import CitationSystem
from app.query.processor import QueryProcessor

logger = logging.getLogger(__name__)


class SearchMode(Enum):
    """Search mode types"""
    WEB = "web"
    AI = "ai"
    RESEARCH = "research"
    DEEP = "deep"


class SearchModes:
    """
    Different search modes with different behaviors
    """
    
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.citation_system = CitationSystem()
        self.rag_engine = None
        self.hybrid_search = None
        logger.info("SearchModes initialized")
    
    def init_engines(self, hybrid_search, rag_engine):
        """Initialize search engines"""
        self.hybrid_search = hybrid_search
        self.rag_engine = rag_engine
        logger.info("Search engines initialized")
    
    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.WEB,
        limit: int = 10
    ) -> Dict:
        """Execute search in the specified mode"""
        processed = self.query_processor.process(query)
        corrected_query = processed['corrected']
        
        logger.info(f"Search mode: {mode.value}, Query: {corrected_query}")
        
        if mode == SearchMode.WEB:
            return await self._web_search(corrected_query, limit)
        elif mode == SearchMode.AI:
            return await self._ai_search(corrected_query, limit)
        elif mode == SearchMode.RESEARCH:
            return await self._research_search(corrected_query, limit)
        elif mode == SearchMode.DEEP:
            return await self._deep_search(corrected_query, limit)
        else:
            return await self._web_search(corrected_query, limit)
    
    async def _web_search(self, query: str, limit: int) -> Dict:
        """Traditional web search"""
        if not self.hybrid_search:
            return {'error': 'Search engine not initialized'}
        
        results = self.hybrid_search.get_top_documents(query, limit)
        
        return {
            'mode': 'web',
            'query': query,
            'results': results,
            'total': len(results),
            'type': 'traditional'
        }
    
    async def _ai_search(self, query: str, limit: int) -> Dict:
        """AI-powered search with answers and citations"""
        if not self.hybrid_search or not self.rag_engine:
            return {'error': 'Search engine not initialized'}
        
        results = self.hybrid_search.get_top_documents(query, limit)
        documents = self._get_documents(results)
        
        ai_result = await self.rag_engine.generate(
            query=query,
            documents=documents,
            include_citations=True
        )
        
        return {
            'mode': 'ai',
            'query': query,
            'answer': ai_result.get('answer', ''),
            'citations': ai_result.get('citations', []),
            'results': results,
            'total': len(results),
            'type': 'ai_powered'
        }
    
    async def _research_search(self, query: str, limit: int) -> Dict:
        """Research mode with multiple sources"""
        if not self.hybrid_search or not self.rag_engine:
            return {'error': 'Search engine not initialized'}
        
        results = self.hybrid_search.get_top_documents(query, limit * 2)
        documents = self._get_documents(results[:limit])
        
        ai_result = await self.rag_engine.generate(
            query=query,
            documents=documents,
            max_documents=5,
            include_citations=True
        )
        
        topics = self._group_by_topic(results)
        
        return {
            'mode': 'research',
            'query': query,
            'answer': ai_result.get('answer', ''),
            'citations': ai_result.get('citations', []),
            'results': results,
            'topics': topics,
            'total': len(results),
            'type': 'research'
        }
    
    async def _deep_search(self, query: str, limit: int) -> Dict:
        """Deep search with iterative refinement"""
        if not self.hybrid_search or not self.rag_engine:
            return {'error': 'Search engine not initialized'}
        
        results = self.hybrid_search.get_top_documents(query, limit)
        follow_ups = self._generate_follow_ups(query, results)
        
        refined_query = f"{query} {' '.join(follow_ups[:2])}"
        refined_results = self.hybrid_search.get_top_documents(refined_query, limit)
        documents = self._get_documents(refined_results[:limit])
        
        ai_result = await self.rag_engine.generate(
            query=query,
            documents=documents,
            max_documents=5,
            include_citations=True
        )
        
        return {
            'mode': 'deep',
            'query': query,
            'refined_query': refined_query,
            'follow_up_questions': follow_ups,
            'answer': ai_result.get('answer', ''),
            'citations': ai_result.get('citations', []),
            'initial_results': results[:5],
            'refined_results': refined_results[:5],
            'total': len(refined_results),
            'type': 'deep_search'
        }
    
    def _get_documents(self, results: List[Dict]) -> List[Dict]:
        """Get full documents from search results"""
        documents = []
        for i, result in enumerate(results[:5]):
            documents.append({
                'id': result.get('id', f'doc{i+1}'),
                'title': result.get('title', 'Untitled'),
                'url': result.get('url', ''),
                'content': result.get('content', '') or 'Sample content for testing.'
            })
        return documents
    
    def _group_by_topic(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """Group results by topic"""
        topics = {}
        topic_keywords = {
            'programming': ['python', 'java', 'javascript', 'code', 'programming'],
            'data': ['data', 'science', 'analytics', 'machine', 'learning'],
            'web': ['web', 'website', 'html', 'css', 'react', 'django'],
            'security': ['security', 'cyber', 'hack', 'encrypt', 'privacy'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'server']
        }
        
        for result in results[:10]:
            title = result.get('title', '').lower()
            topic = 'general'
            
            for topic_name, keywords in topic_keywords.items():
                if any(kw in title for kw in keywords):
                    topic = topic_name
                    break
            
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(result)
        
        return topics
    
    def _generate_follow_ups(self, query: str, results: List[Dict]) -> List[str]:
        """Generate follow-up questions"""
        follow_ups = []
        
        if not results:
            return ["Try rephrasing your query", "Use more specific terms"]
        
        for result in results[:3]:
            title = result.get('title', '')
            if title:
                follow_ups.append(f"Tell me more about {title[:30]}")
        
        if len(follow_ups) < 3:
            follow_ups.append("What are the key concepts?")
            follow_ups.append("Show me examples")
        
        return follow_ups[:3]

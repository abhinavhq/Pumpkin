"""
Grounded Answers - Fact-check and verify AI responses
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class GroundedAnswer:
    """
    Ensure AI answers are grounded in source documents
    """
    
    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold
        logger.info("GroundedAnswer initialized")
    
    def process(
        self,
        answer: str,
        sources: List[Dict],
        query: str
    ) -> Dict:
        """
        Process an answer to make it grounded
        """
        # 1. Extract facts from the answer
        facts = self._extract_facts(answer)
        
        # 2. Verify each fact against sources
        verified_facts = self._verify_facts(facts, sources)
        
        # 3. Calculate confidence
        confidence = self._calculate_confidence(verified_facts)
        
        # 4. Build grounded answer
        grounded_answer = self._build_grounded_answer(
            answer, verified_facts, sources, confidence
        )
        
        # 5. Add verification metadata
        grounded_answer.update({
            'confidence': confidence,
            'verified_facts': verified_facts,
            'total_facts': len(facts),
            'sources_used': len(sources)
        })
        
        return grounded_answer
    
    def _extract_facts(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        sentences = re.split(r'[.!?]+', text)
        facts = [s.strip() for s in sentences if len(s.strip()) > 20]
        return facts
    
    def _verify_facts(
        self,
        facts: List[str],
        sources: List[Dict]
    ) -> List[Dict]:
        """Verify each fact against sources"""
        verified = []
        
        for fact in facts:
            matches = []
            for source in sources:
                content = source.get('content', '').lower()
                fact_words = set(fact.lower().split())
                stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'to', 'for', 'with', 'on', 'at', 'from', 'by'}
                fact_words = fact_words - stop_words
                
                if fact_words:
                    source_words = set(content.split())
                    overlap = fact_words & source_words
                    if len(overlap) / len(fact_words) > 0.3:
                        matches.append({
                            'source': source,
                            'overlap': len(overlap),
                            'total_words': len(fact_words)
                        })
            
            verified.append({
                'fact': fact,
                'verified': len(matches) > 0,
                'matches': matches,
                'match_count': len(matches)
            })
        
        return verified
    
    def _calculate_confidence(self, verified_facts: List[Dict]) -> float:
        """Calculate confidence score based on verification"""
        if not verified_facts:
            return 0.0
        
        verified_count = sum(1 for f in verified_facts if f['verified'])
        confidence = verified_count / len(verified_facts)
        return min(1.0, confidence)
    
    def _build_grounded_answer(
        self,
        answer: str,
        verified_facts: List[Dict],
        sources: List[Dict],
        confidence: float
    ) -> Dict:
        """Build the final grounded answer"""
        if not sources or confidence < self.confidence_threshold:
            return {
                'answer': "I couldn't find enough reliable information to answer this question. Please try rephrasing your query or check the search results below.",
                'is_grounded': False,
                'reason': 'insufficient_evidence'
            }
        
        if confidence > 0.7:
            confidence_text = self._get_confidence_text(confidence)
            return {
                'answer': f"{answer}\n\n{confidence_text}",
                'is_grounded': True,
                'reason': 'verified'
            }
        
        return {
            'answer': f"{answer}\n\n⚠️ Some information may not be fully verified. Please check the sources below.",
            'is_grounded': True,
            'reason': 'partial_verification'
        }
    
    def _get_confidence_text(self, confidence: float) -> str:
        """Get confidence text based on score"""
        if confidence > 0.9:
            return "✅ High confidence - Information verified across multiple sources."
        elif confidence > 0.7:
            return "✅ Moderate confidence - Information appears in sources."
        elif confidence > 0.5:
            return "⚠️ Low confidence - Limited verification available."
        else:
            return "❌ Unable to verify - Please verify information independently."

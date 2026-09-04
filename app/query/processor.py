"""
Query Processor - Understand and enhance user queries
"""

import re
import logging
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class QueryProcessor:
    """
    Process and understand user queries:
    - Spelling correction
    - Query expansion
    - Intent detection
    - Entity extraction
    """
    
    def __init__(self):
        self.spelling_dict = self._init_spelling_dict()
        self.synonyms = self._init_synonyms()
        self.intent_patterns = self._init_intent_patterns()
        self.entity_patterns = self._init_entity_patterns()
        logger.info("QueryProcessor initialized")
    
    def process(self, query: str) -> Dict:
        if not query:
            return {
                'original': '',
                'corrected': '',
                'expanded': [],
                'intent': 'unknown',
                'entities': [],
                'tokens': []
            }
        
        corrected = self.correct_spelling(query)
        tokens = self._tokenize(corrected)
        expanded = self.expand_query(tokens)
        intent = self.detect_intent(corrected)
        entities = self.extract_entities(corrected)
        
        return {
            'original': query,
            'corrected': corrected,
            'expanded': expanded,
            'intent': intent,
            'entities': entities,
            'tokens': tokens
        }
    
    def correct_spelling(self, query: str) -> str:
        words = query.lower().split()
        corrected_words = []
        
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word in self.spelling_dict:
                corrected_words.append(self.spelling_dict[clean_word])
            else:
                corrected = self._find_similar_word(clean_word)
                corrected_words.append(corrected if corrected else clean_word)
        
        return ' '.join(corrected_words)
    
    def expand_query(self, tokens: List[str]) -> List[str]:
        expanded = list(tokens)
        for token in tokens:
            if token in self.synonyms:
                expanded.extend(self.synonyms[token])
        
        seen = set()
        unique = []
        for token in expanded:
            if token not in seen:
                seen.add(token)
                unique.append(token)
        return unique
    
    def detect_intent(self, query: str) -> str:
        query_lower = query.lower()
        for pattern, intent in self.intent_patterns:
            if re.search(pattern, query_lower):
                return intent
        return 'informational'
    
    def extract_entities(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, query_lower)
                for match in matches:
                    if not any(e['text'] == match for e in entities):
                        entities.append({
                            'text': match,
                            'type': entity_type
                        })
        return entities
    
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'[a-zA-Z0-9]+', text.lower())
    
    def _find_similar_word(self, word: str) -> Optional[str]:
        if len(word) < 3:
            return None
        for key, value in self.spelling_dict.items():
            if key in word or word in key:
                if len(key) >= len(word) - 2:
                    return value
        return None
    
    def _init_spelling_dict(self) -> Dict[str, str]:
        return {
            'pythn': 'python',
            'pyton': 'python',
            'pthon': 'python',
            'javascrpt': 'javascript',
            'programing': 'programming',
            'developement': 'development',
            'datascience': 'data science',
            'machinelearning': 'machine learning',
            'artificialintelligence': 'artificial intelligence',
            'begginer': 'beginner',
            'tutoral': 'tutorial',
            'gide': 'guide',
            'intermediat': 'intermediate',
        }
    
    def _init_synonyms(self) -> Dict[str, List[str]]:
        return {
            'python': ['py', 'python3'],
            'java': ['java', 'jdk'],
            'javascript': ['js', 'ecmascript'],
            'programming': ['coding', 'development'],
            'data': ['dataset', 'information', 'analytics'],
            'science': ['research', 'study'],
            'machine': ['ml'],
            'learning': ['training', 'education'],
            'web': ['website', 'internet'],
            'development': ['dev', 'building'],
            'cloud': ['aws', 'azure'],
            'security': ['cybersecurity', 'protection'],
            'database': ['db', 'sql'],
            'analytics': ['analysis', 'statistics'],
            'api': ['rest', 'graphql']
        }
    
    def _init_intent_patterns(self) -> List[Tuple[str, str]]:
        return [
            (r'\b(how to|what is|why is|when is|who is|learn|tutorial|guide)\b', 'informational'),
            (r'\b(explain|understanding|introduction|basics|beginner)\b', 'informational'),
            (r'\b(website|site|homepage|official|login)\b', 'navigational'),
            (r'\b(buy|purchase|price|cost|download|install|get|order)\b', 'transactional'),
            (r'\b(vs|versus|compare|difference|better than)\b', 'comparison'),
        ]
    
    def _init_entity_patterns(self) -> Dict[str, List[str]]:
        return {
            'language': [
                r'\b(python|java|javascript|ruby|go|rust|c\+\+|php|swift|kotlin)\b'
            ],
            'framework': [
                r'\b(django|flask|react|angular|vue|spring|node|express|rails)\b'
            ],
            'technology': [
                r'\b(ai|ml|cloud|docker|kubernetes|aws|azure|gcp|linux|git)\b'
            ],
            'topic': [
                r'\b(web|data|security|networking|database|analytics|devops)\b'
            ]
        }

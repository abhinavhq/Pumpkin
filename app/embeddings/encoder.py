"""
Text Encoder - Convert text to vector embeddings using Sentence Transformers
"""

import logging
import numpy as np
from typing import List, Optional
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class TextEncoder:
    """
    Encode text into vector embeddings using a pre-trained model
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the text encoder with a Sentence Transformer model
        
        Available models:
        - all-MiniLM-L6-v2: Fast, 384-dim embeddings (default)
        - all-mpnet-base-v2: Better quality, 768-dim embeddings (slower)
        - multi-qa-MiniLM-L6-cos-v1: Optimized for similarity search
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Sentence Transformer model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Model loaded. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def encode(self, text: str) -> np.ndarray:
        """
        Encode a single text into a vector embedding
        """
        if not text:
            return np.zeros(self.model.get_sentence_embedding_dimension())
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return np.zeros(self.model.get_sentence_embedding_dimension())
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts into vector embeddings
        """
        if not texts:
            return np.array([])
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding batch: {e}")
            return np.array([])
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.model.get_sentence_embedding_dimension() if self.model else 0

"""
Search API Routes - Search endpoints for the search engine
"""

import logging
import time
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.indexing.bm25 import BM25
from app.database.database import Database
from app.database.repositories import DocumentRepository
from app.analytics.analytics import SearchAnalytics

logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()

# Global search engine instance
search_engine: Optional[BM25] = None
doc_repo: Optional[DocumentRepository] = None


def initialize_search_engine(db_path: str = "data/search.db"):
    """Initialize the search engine with documents from the database"""
    global search_engine, doc_repo
    
    logger.info("Initializing search engine...")
    
    # Connect to database
    db = Database(db_path)
    doc_repo = DocumentRepository(db)
    
    # Create BM25 search engine
    search_engine = BM25(k1=1.2, b=0.75)
    
    # Load documents from database
    documents = doc_repo.get_all(limit=1000)
    logger.info(f"Loaded {len(documents)} documents from database")
    
    # Index documents
    for doc in documents:
        content = doc.content or ""
        search_engine.add_document(
            doc_id=str(doc.id),
            title=doc.title or "",
            content=content
        )
    
    stats = search_engine.get_stats()
    logger.info(f"Search engine initialized: {stats['total_documents']} documents, {stats['unique_terms']} unique terms")
    
    return search_engine


# --- Models ---

class SearchResult(BaseModel):
    id: str
    title: str
    score: float
    total_terms: int
    unique_terms: int


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total_results: int
    took: float


# --- Endpoints ---

@router.get("/search")
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return")
):
    """Search for documents matching the query"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    start_time = time.time()
    
    results = search_engine.get_top_documents(q, limit=limit)
    
    took = (time.time() - start_time) * 1000
    
    # Track analytics
    try:
        analytics = SearchAnalytics()
        analytics.track_search(
            query=q,
            results_count=len(results),
            latency_ms=took,
            mode="web"
        )
    except Exception as e:
        logger.warning(f"Failed to track analytics: {e}")
    
    return SearchResponse(
        query=q,
        results=[
            SearchResult(
                id=r['id'],
                title=r['title'],
                score=r['score'],
                total_terms=r['total_terms'],
                unique_terms=r['unique_terms']
            )
            for r in results
        ],
        total_results=len(results),
        took=round(took, 2)
    )


@router.get("/search/stats")
async def search_stats():
    """Get search engine statistics"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    stats = search_engine.get_stats()
    return {
        "status": "ready",
        "stats": stats
    }


@router.get("/search/explain")
async def explain_search(
    q: str = Query(..., min_length=1),
    doc_id: str = Query(..., description="Document ID to explain")
):
    """Explain why a specific document scored for a query"""
    if not search_engine:
        raise HTTPException(status_code=503, detail="Search engine not initialized")
    
    explanation = search_engine.explain_score(doc_id, q)
    
    if 'error' in explanation:
        raise HTTPException(status_code=404, detail=explanation['error'])
    
    return explanation
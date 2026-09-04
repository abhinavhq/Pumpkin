"""
AI Search Engine - Main Application Entry Point
"""

import logging
import sys
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from app.api.routes_search import router as search_router
from app.api.routes_autocomplete import router as autocomplete_router
from app.api.routes_related import router as related_router
from app.api.routes_search import initialize_search_engine

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="AI Search Engine",
    description="A 10/10 AI-powered search engine built from scratch",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    search_engine_ready: bool = False

# --- Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# --- Include Routers ---
app.include_router(search_router, prefix="/api/v1")
app.include_router(autocomplete_router, prefix="/api/v1")
app.include_router(related_router, prefix="/api/v1")

# --- Startup Event ---
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    try:
        initialize_search_engine("data/search.db")
        logger.info("Search engine initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize search engine: {e}")

# --- Endpoints ---
@app.get("/")
async def root():
    return {
        "name": "AI Search Engine",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health",
        "search": "/api/v1/search?q=python",
        "autocomplete": "/api/v1/autocomplete?q=pyt",
        "related": "/api/v1/related?q=python",
        "message": "Building a 10/10 search engine from scratch! 🚀"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    search_ready = False
    try:
        from app.api.routes_search import search_engine
        search_ready = search_engine is not None
    except:
        pass
    
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version="0.1.0",
        search_engine_ready=search_ready
    )

# --- Development server entry point ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
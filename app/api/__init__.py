"""API module for REST endpoints"""

from .routes_search import router as search_router
from .routes_autocomplete import router as autocomplete_router
from .routes_related import router as related_router

__all__ = ['search_router', 'autocomplete_router', 'related_router']
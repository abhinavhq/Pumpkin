"""
URL Utilities - Normalization, validation, and parsing
"""

import re
from urllib.parse import urlparse, urljoin, urlunparse


def normalize_url(url: str) -> str:
    """
    Normalize a URL by:
    - Removing fragments (#section)
    - Converting to lowercase
    - Ensuring trailing slash consistency
    - Removing www prefix
    """
    if not url:
        return url
    
    parsed = urlparse(url)
    
    # Remove fragment
    parsed = parsed._replace(fragment="")
    
    # Lowercase scheme and netloc
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    
    # Remove www prefix
    if netloc.startswith("www."):
        netloc = netloc[4:]
    
    # Remove trailing slash if path is empty or just /
    path = parsed.path
    if path.endswith("/") and len(path) > 1:
        path = path[:-1]
    
    # Reconstruct URL
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    
    return normalized


def is_valid_url(url: str) -> bool:
    """Check if URL has a valid scheme and format"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def get_domain(url: str) -> str:
    """Extract domain from URL"""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return ""


def is_internal_link(base_url: str, link: str) -> bool:
    """Check if a link is internal to the same domain"""
    base_domain = get_domain(base_url)
    link_domain = get_domain(link)
    return base_domain == link_domain


def resolve_relative_url(base_url: str, relative_url: str) -> str:
    """Convert relative URL to absolute URL"""
    try:
        return urljoin(base_url, relative_url)
    except Exception:
        return relative_url


def is_same_url(url1: str, url2: str) -> bool:
    """Check if two URLs are the same (normalized)"""
    return normalize_url(url1) == normalize_url(url2)


def is_html_content(content_type: str) -> bool:
    """Check if content type is HTML"""
    return content_type and (
        "text/html" in content_type or 
        "application/xhtml+xml" in content_type
    )


def extract_base_url(url: str) -> str:
    """Extract the base URL (scheme + domain)"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
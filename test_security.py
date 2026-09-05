"""
Test script for security features
"""

import time
from app.security.input_validator import InputValidator
from app.security.rate_limiter import RateLimiter


def test_input_validator():
    """Test input validator"""
    
    print("\n" + "="*50)
    print("🛡️ TESTING INPUT VALIDATOR")
    print("="*50 + "\n")
    
    validator = InputValidator()
    
    test_cases = [
        ("python programming", "python programming"),
        ("<script>alert('xss')</script>", "script alert  xss  script"),
        ("SELECT * FROM users", None),
        ("DROP TABLE users", None),
        ("' OR '1'='1", None),
        ("normal query with spaces", "normal query with spaces"),
        ("", None),
        ("a" * 600, None),  # Too long
    ]
    
    for input_text, expected in test_cases:
        result = validator.sanitize_query(input_text)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{input_text[:30]}' → '{result}' (Expected: '{expected}')")
    
    print("\n" + "="*50)
    print("✅ Input validator test complete!")
    print("="*50 + "\n")


def test_rate_limiter():
    """Test rate limiter"""
    
    print("\n" + "="*50)
    print("🚦 TESTING RATE LIMITER")
    print("="*50 + "\n")
    
    limiter = RateLimiter(max_requests=5, time_window=10, block_duration=5)
    client_ip = "127.0.0.1"
    
    print(f"Testing rate limiter for IP: {client_ip}")
    print(f"Max requests: 5 per 10 seconds\n")
    
    for i in range(8):
        allowed = limiter.is_allowed(client_ip)
        stats = limiter.get_stats(client_ip)
        
        status = "✅" if allowed else "❌"
        print(f"  Request {i+1}: {status} (requests: {stats['requests']}/{stats['max_requests']})")
        
        if not allowed:
            print(f"    ⚠️ Blocked! Waiting 1 second...")
            time.sleep(1)
            
            # Try again
            allowed = limiter.is_allowed(client_ip)
            if allowed:
                print(f"    ✅ Unblocked after wait")
            else:
                stats = limiter.get_stats(client_ip)
                print(f"    ❌ Still blocked (remaining: {stats['remaining']})")
    
    print("\n" + "="*50)
    print("✅ Rate limiter test complete!")
    print("="*50 + "\n")


def test_url_validator():
    """Test URL validator (SSRF protection)"""
    
    print("\n" + "="*50)
    print("🔗 TESTING URL VALIDATOR (SSRF Protection)")
    print("="*50 + "\n")
    
    validator = InputValidator()
    
    urls = [
        ("https://example.com", True),
        ("http://google.com", True),
        ("http://127.0.0.1/admin", False),
        ("https://localhost:8080", False),
        ("http://192.168.1.1/config", False),
        ("file:///etc/passwd", False),
        ("gopher://internal-server", False),
        ("https://github.com", True),
    ]
    
    for url, expected in urls:
        result = validator.validate_url(url)
        status = "✅" if result == expected else "❌"
        print(f"{status} '{url}' → {result} (Expected: {expected})")
    
    print("\n" + "="*50)
    print("✅ URL validator test complete!")
    print("="*50 + "\n")


if __name__ == "__main__":
    test_input_validator()
    test_rate_limiter()
    test_url_validator()
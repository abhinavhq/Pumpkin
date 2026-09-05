"""
Rate Limiter - Prevent API abuse
"""

import time
import logging
from typing import Dict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limit requests per IP address
    """
    
    def __init__(
        self,
        max_requests: int = 60,
        time_window: int = 60,
        block_duration: int = 300
    ):
        self.max_requests = max_requests
        self.time_window = time_window
        self.block_duration = block_duration
        
        self.requests: Dict[str, list] = defaultdict(list)
        self.blocked_ips: Dict[str, float] = {}
        
        logger.info(f"RateLimiter initialized: max={max_requests}, window={time_window}s")
    
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        
        if client_ip in self.blocked_ips:
            if now - self.blocked_ips[client_ip] > self.block_duration:
                del self.blocked_ips[client_ip]
            else:
                logger.warning(f"Blocked request from {client_ip}")
                return False
        
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < self.time_window
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            self.blocked_ips[client_ip] = now
            logger.warning(f"Rate limit exceeded for {client_ip}, blocking")
            return False
        
        self.requests[client_ip].append(now)
        return True
    
    def get_stats(self, client_ip: str) -> Dict:
        now = time.time()
        
        self.requests[client_ip] = [
            t for t in self.requests[client_ip]
            if now - t < self.time_window
        ]
        
        return {
            'ip': client_ip,
            'requests': len(self.requests[client_ip]),
            'max_requests': self.max_requests,
            'time_window': self.time_window,
            'is_blocked': client_ip in self.blocked_ips,
            'remaining': max(0, self.max_requests - len(self.requests[client_ip]))
        }
    
    def reset(self, client_ip: str):
        if client_ip in self.requests:
            del self.requests[client_ip]
        if client_ip in self.blocked_ips:
            del self.blocked_ips[client_ip]
        logger.info(f"Rate limit reset for {client_ip}")

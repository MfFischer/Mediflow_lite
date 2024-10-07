"""
Rate limiting middleware for API endpoints.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import asyncio

from .config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware.
    
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, app, calls: int = None, period: int = 60):
        super().__init__(app)
        self.calls = calls or settings.rate_limit_per_minute
        self.period = period  # seconds
        self.clients: Dict[str, list[datetime]] = defaultdict(list)
        self.cleanup_task = None
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting."""
        
        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)
        
        # Get client identifier (IP address)
        client_ip = request.client.host
        
        # Clean up old entries
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period)
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if timestamp > cutoff
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.calls} requests per {self.period} seconds."
            )
        
        # Add current request timestamp
        self.clients[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(
            self.calls - len(self.clients[client_ip])
        )
        response.headers["X-RateLimit-Reset"] = str(
            int((now + timedelta(seconds=self.period)).timestamp())
        )
        
        return response
    
    async def cleanup_old_entries(self):
        """Periodically clean up old entries to prevent memory leak."""
        while True:
            await asyncio.sleep(self.period)
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.period * 2)
            
            # Remove clients with no recent requests
            clients_to_remove = [
                client for client, timestamps in self.clients.items()
                if not timestamps or max(timestamps) < cutoff
            ]
            
            for client in clients_to_remove:
                del self.clients[client]


"""
Request tracking middleware for MediFlow Lite.

Provides:
- Request ID generation and tracking
- Request/response logging
- Performance monitoring
- Error tracking
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging_config import request_id_var

logger = logging.getLogger('mediflow.requests')


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track requests with unique IDs and log request/response details.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add tracking information.
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)
        
        # Store request ID in request state
        request.state.request_id = request_id
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Start timer
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Incoming request: {request.method} {request.url.path}",
            extra={
                'request_id': request_id,
                'method': request.method,
                'endpoint': request.url.path,
                'ip_address': client_ip,
                'user_agent': request.headers.get('user-agent', 'unknown'),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - {response.status_code}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'endpoint': request.url.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration_ms, 2),
                    'ip_address': client_ip,
                }
            )
            
            # Log slow requests (> 1 second)
            if duration_ms > 1000:
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} took {duration_ms:.2f}ms",
                    extra={
                        'request_id': request_id,
                        'method': request.method,
                        'endpoint': request.url.path,
                        'duration_ms': round(duration_ms, 2),
                        'event_type': 'slow_request',
                    }
                )
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(e)}",
                extra={
                    'request_id': request_id,
                    'method': request.method,
                    'endpoint': request.url.path,
                    'duration_ms': round(duration_ms, 2),
                    'ip_address': client_ip,
                    'error': str(e),
                    'event_type': 'request_error',
                },
                exc_info=True
            )
            
            # Re-raise exception
            raise
        
        finally:
            # Clear request ID from context
            request_id_var.set(None)


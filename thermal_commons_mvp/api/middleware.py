"""Rate limiting middleware for FastAPI."""

import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from thermal_commons_mvp.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._request_times: dict[str, list[float]] = defaultdict(list)
        self._cleanup_interval = 60.0  # Clean up old entries every 60 seconds
        self._last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean up old entries periodically
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._cleanup_old_entries(current_time)
            self._last_cleanup = current_time
        
        # Check rate limit
        if not self._is_allowed(client_ip, current_time):
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": "60"},
            )
        
        # Process request
        response = await call_next(request)
        return response

    def _is_allowed(self, client_ip: str, current_time: float) -> bool:
        """Check if request is within rate limit."""
        # Remove requests older than 1 minute
        cutoff_time = current_time - 60.0
        self._request_times[client_ip] = [
            t for t in self._request_times[client_ip] if t > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self._request_times[client_ip]) >= self.requests_per_minute:
            return False
        
        # Record this request
        self._request_times[client_ip].append(current_time)
        return True

    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove old entries to prevent memory leak."""
        cutoff_time = current_time - 60.0
        for ip in list(self._request_times.keys()):
            self._request_times[ip] = [
                t for t in self._request_times[ip] if t > cutoff_time
            ]
            # Remove IP if no recent requests
            if not self._request_times[ip]:
                del self._request_times[ip]

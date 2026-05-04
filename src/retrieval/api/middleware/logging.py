"""
Request logging middleware
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests and responses"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        print(f"[{request.method}] {request.url.path}")

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        print(f"[{request.method}] {request.url.path} - {response.status_code} ({duration:.3f}s)")

        # Add timing header
        response.headers["X-Response-Time"] = str(duration)

        return response

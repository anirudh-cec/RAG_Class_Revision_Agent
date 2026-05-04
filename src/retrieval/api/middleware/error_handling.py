"""
Global exception handler
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime


async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""

    error_response = {
        "error": "Internal Server Error",
        "message": str(exc),
        "timestamp": datetime.now().isoformat(),
        "path": str(request.url.path)
    }

    return JSONResponse(
        status_code=500,
        content=error_response
    )

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get("X-Correlation-ID")
            or request.headers.get("X-Co-Relation-Id")
            or str(uuid.uuid4())
        )

        # Attach correlation ID to request.state
        request.state.correlation_id = correlation_id

        # Add correlation ID to response header
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id

        return response

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Client-provided or generate new
        correlation_id = (
            request.headers.get("x-correlation-id")
            or request.headers.get("x-co-relation-id")
            or str(uuid.uuid4())
        )

        # Store in request.state 
        request.state.correlation_id = correlation_id

        # Execute request
        response = await call_next(request)

        # Add header to response
        response.headers["x-correlation-id"] = correlation_id
        return response

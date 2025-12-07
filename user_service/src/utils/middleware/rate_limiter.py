import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 5, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.ip_store = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()

        if client_ip not in self.ip_store:
            self.ip_store[client_ip] = []

        self.ip_store[client_ip] = [
            t for t in self.ip_store[client_ip]
            if now - t < self.window_seconds
        ]

        if len(self.ip_store[client_ip]) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": "Too Many Requests",
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                }
            )

        self.ip_store[client_ip].append(now)
        return await call_next(request)

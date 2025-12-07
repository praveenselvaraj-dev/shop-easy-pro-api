import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import setup_logger

logger = setup_logger("exception-middleware")

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        try:
            return await call_next(request)

        except Exception as e:
            correlation_id = getattr(request.state, "correlation_id", "N/A")

            logger.error({
                "error": str(e),
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "trace": traceback.format_exc()
            })

            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Internal Server Error",
                    "detail": str(e),
                    "correlation_id": correlation_id,
                },
            )
    
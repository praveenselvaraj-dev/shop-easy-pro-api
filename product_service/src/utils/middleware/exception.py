import traceback
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import setup_logger

logger = setup_logger("exception-middleware")


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # Process the request
            return await call_next(request)

        except Exception as exc:
            # Get correlation ID if available
            correlation_id = getattr(request.state, "correlation_id", "N/A")

            # Default values for unknown exceptions
            status_code = 500
            message = "Internal Server Error"
            detail = str(exc)

            # If the exception has a custom status_code and message (our custom exceptions)
            if hasattr(exc, "status_code"):
                status_code = getattr(exc, "status_code", 500)
                message = getattr(exc, "message", message)

            # Log the exception with correlation ID
            logger.error({
                "type": type(exc).__name__,
                "error": str(exc),
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "trace": traceback.format_exc()
            })

            # Return structured JSON response
            return JSONResponse(
                status_code=status_code,
                content={
                    "status": "error",
                    "message": message,
                    "detail": detail,
                    "correlation_id": correlation_id
                }
            )

import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logger import setup_logger

logger = setup_logger("exception-middleware")

class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)

        except HTTPException as http_exc:
            correlation_id = getattr(request.state, "correlation_id", "N/A")

            logger.warning({
                "type": "HTTPException",
                "status_code": http_exc.status_code,
                "detail": http_exc.detail,
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method
            })

            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "status": "fail",
                    "message": http_exc.detail,
                    "correlation_id": correlation_id
                }
            )

        except Exception as exc:
            correlation_id = getattr(request.state, "correlation_id", "N/A")

            # Default response
            status_code = 500
            message = "Internal Server Error"
            detail = str(exc)

            # Business exceptions
            if hasattr(exc, "status_code"):
                status_code = exc.status_code
                message = exc.message

            logger.error({
                "type": type(exc).__name__,
                "error": str(exc),
                "correlation_id": correlation_id,
                "path": request.url.path,
                "method": request.method,
                "trace": traceback.format_exc()
            })

            return JSONResponse(
                status_code=status_code,
                content={
                    "status": "error",
                    "message": message,
                    "detail": detail,
                    "correlation_id": correlation_id
                }
            )

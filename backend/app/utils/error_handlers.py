import uuid
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.schemas.common import ErrorDetail, ErrorResponse
from app.utils.exceptions import AppException, ErrorCode


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    request_id = get_request_id(request)
    logger.warning(
        "Application error | request_id={} | code={} | message={}",
        request_id,
        exc.error_code.value,
        exc.message,
    )

    details = [
        ErrorDetail(
            field=item.get("field"),
            message=item.get("message", ""),
            code=item.get("code"),
        )
        for item in exc.details
    ] or None

    response = ErrorResponse(
        error=exc.error_code.value,
        message=exc.message,
        details=details,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    request_id = get_request_id(request)
    logger.warning(
        "HTTP error | request_id={} | status={} | detail={}",
        request_id,
        exc.status_code,
        exc.detail,
    )

    response = ErrorResponse(
        error=ErrorCode.NOT_FOUND.value if exc.status_code == 404 else "HTTPException",
        message=str(exc.detail),
        request_id=request_id,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(),
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    request_id = get_request_id(request)
    logger.warning(
        "Validation error | request_id={} | errors={}",
        request_id,
        exc.errors(),
    )

    details = [
        ErrorDetail(
            field=".".join(str(part) for part in error.get("loc", []) if part != "body"),
            message=error.get("msg", "Validation error"),
            code=ErrorCode.VALIDATION_ERROR.value,
        )
        for error in exc.errors()
    ]

    response = ErrorResponse(
        error=ErrorCode.VALIDATION_ERROR.value,
        message="Request validation failed",
        details=details,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response.model_dump(),
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    request_id = get_request_id(request)
    logger.exception(
        "Unhandled exception | request_id={} | error={}",
        request_id,
        str(exc),
    )

    response = ErrorResponse(
        error=ErrorCode.INTERNAL_ERROR.value,
        message="An unexpected error occurred",
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(),
    )


def register_exception_handlers(app: Any) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

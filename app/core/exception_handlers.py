import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException


logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    logger.warning(
        "%s %s -> %s",
        request.method,
        request.url.path,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "Validation error: %s",
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed.",
            "details": exc.errors(),
        },
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception("Unhandled exception")

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error.",
        },
    )

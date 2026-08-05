from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logger import app_logger
from app.api.router import router
from app.core.exceptions import AppException

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.middleware.security_headers import (
    SecurityHeadersMiddleware,
)
from fastapi.exceptions import (
    RequestValidationError,
)

from fastapi import HTTPException

from app.core.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.include_router(router, prefix=f"/api/{settings.API_VERSION}")

app.add_middleware(
    SecurityHeadersMiddleware,
)


@app.on_event("startup")
async def startup():

    app_logger.info("Application Started")


@app.get("/")
def root():

    return {"application": settings.APP_NAME, "version": settings.API_VERSION}


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    # If exc is a tuple like ('Invalid email or password.', 401)
    message = exc.args[0] if exc.args else "An error occurred"
    status_code = exc.args[1] if len(exc.args) > 1 else 400

    return JSONResponse(
        status_code=status_code,
        content={"detail": message},
    )

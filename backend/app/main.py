from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.api.router import api_router
from app.core.config import get_settings
from app.schemas.errors import ErrorResponse, ErrorPayload

settings = get_settings()

app = FastAPI(title=settings.PROJECT_NAME)

# --------------------
# CORS
# --------------------
allow_origins = settings.CORS_ORIGINS
allow_all = allow_origins == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False if allow_all else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Routes
# --------------------
app.include_router(api_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# --------------------
# Error handlers
# --------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    payload = ErrorResponse(
        error=ErrorPayload(
            code=f"HTTP_{exc.status_code}",
            message="Request failed",
            detail=exc.detail,
        )
    )
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump())


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    payload = ErrorResponse(
        error=ErrorPayload(
            code="DB_INTEGRITY_ERROR",
            message="Database constraint error",
            detail=str(exc.orig) if exc.orig else str(exc),
        )
    )
    return JSONResponse(status_code=409, content=payload.model_dump())


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    payload = ErrorResponse(
        error=ErrorPayload(
            code="UNHANDLED_ERROR",
            message="Internal server error",
        )
    )
    return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=payload.model_dump())
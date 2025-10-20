import logging
from contextlib import asynccontextmanager

from config import settings
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from routers import chat, files, sessions, ws
from services.file import FileService
from utils.database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    FileService.ensure_upload_dir()
    yield


app = FastAPI(
    title="Compuer Use v2 API",
    description="API for computer use demo with task execution and file management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(sessions.router)
app.include_router(files.router)
app.include_router(ws.router)
app.include_router(chat.router)

# Mount static files
app.mount(
    "/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads"
)


@app.get("/")
async def root():
    return {"message": "Computer Use v2 API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error(
        f"HTTP {exc.status_code} error for {request.method} {request.url.path}: {exc.detail}",
        extra={"path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_msg = (
        f"Unhandled error for {request.method} {request.url.path}: {str(exc)}"
    )
    logging.exception(error_msg)
    return JSONResponse(
        status_code=500,
        content={"detail": error_msg},
    )

"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import categories, tasks
from .config import get_settings
from .database import init_db

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: Cleanup if needed
    pass


# Create FastAPI application
app = FastAPI(
    title="Todo App API",
    description="Phase II Full-Stack Web Application Todo App",
    version="2.0.0",
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


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "Todo App API",
        "version": "2.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(tasks.router)
app.include_router(categories.router)

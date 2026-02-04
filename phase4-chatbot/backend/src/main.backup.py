"""FastAPI application entry point for AI-powered todo chatbot."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from .config import settings
from .api import chat_router
from .mcp import mcp_server

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events.

    Handles:
    - MCP server initialization and shutdown
    - OpenAI client initialization
    - Database connection management
    """
    # Startup
    logger.info("Starting AI-powered todo chatbot backend...")

    try:
        # Initialize Gemini client with OpenAI-compatible endpoint
        gemini_client = AsyncOpenAI(
            
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )
        app.state.gemini_client = gemini_client
        logger.info(f"Gemini client initialized with model: {settings.gemini_model}")

        # Initialize MCP server
        await mcp_server.initialize()
        logger.info("MCP server initialized")

        logger.info("Application startup complete")

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")

    try:
        # Shutdown MCP server
        await mcp_server.shutdown()
        logger.info("MCP server shutdown complete")

        logger.info("Application shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title="AI Todo Chatbot API",
    description="Chat endpoint for natural language task management using MCP and OpenAI Agents SDK",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router)


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Dict with status information
    """
    return {
        "status": "healthy",
        "service": "todo-chatbot-backend",
        "version": "1.0.0",
        "mcp_initialized": mcp_server.is_initialized()
    }


@app.get("/")
async def root():
    """Root endpoint with API information.

    Returns:
        Dict with API information
    """
    return {
        "message": "AI-Powered Todo Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=settings.debug
    )

"""Fixed FastAPI main application with OpenAI Agents SDK + Gemini.

This implementation properly configures Gemini API via OpenAI-compatible
endpoint and uses the agent service with tool calling support.
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from .api.chat import router as chat_router
from .database import engine
from .models import SQLModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global OpenAI client for Gemini
gemini_client: AsyncOpenAI = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting application...")

    # Initialize database tables
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created/verified")

    # Initialize Gemini client via OpenAI-compatible endpoint
    global gemini_client
    gemini_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        timeout=float(os.getenv("LLM_REQUEST_TIMEOUT", "30")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "3"))
    )
    logger.info(f"Gemini client initialized with base_url: {gemini_client.base_url}")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await gemini_client.close()


# Create FastAPI app
app = FastAPI(
    title="Todo AI Chatbot API",
    description="AI-powered todo management with OpenAI Agents SDK + Gemini",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info(f"CORS configured for origins: {cors_origins}")


# Register routers
app.include_router(chat_router, prefix="/api", tags=["chat"])


# Dependency to get Gemini client
def get_gemini_client() -> AsyncOpenAI:
    """Get the global Gemini client instance.

    Returns:
        AsyncOpenAI client configured for Gemini
    """
    return gemini_client


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Status information
    """
    return {
        "status": "healthy",
        "service": "todo-chatbot",
        "llm": "gemini-2.0-flash-exp",
        "framework": "openai-agents-sdk"
    }


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Todo AI Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8002"))
    uvicorn.run(
        "src.main_fixed:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

"""
Smart Delivery Route Optimization — FastAPI Application
════════════════════════════════════════════════════════
Main application entry point. Serves API endpoints,
manages database lifecycle, and enables CORS for frontend.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.db.session import init_db
from app.api.routes import datasets, optimization, bigdata

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing Smart Delivery Route Optimization Engine...")
    logger.info(f"Environment: {settings.ENVIRONMENT}, Debug: {settings.DEBUG}")

    # Ensure required directories exist
    for directory in [
        settings.DATA_DIR,
        settings.RAW_DATA_DIR,
        settings.PROCESSED_DATA_DIR,
        settings.RESULTS_DIR,
        settings.UPLOAD_DIR,
    ]:
        os.makedirs(directory, exist_ok=True)

    # Initialize database
    try:
        await init_db()
        logger.info("Database schema verified and initialized.")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    yield

    logger.info("Shutting down Smart Delivery Route Optimization Engine...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hybrid Big Data + Quantum Computing Delivery Route Optimization System",
    lifespan=lifespan,
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(datasets.router)
app.include_router(optimization.router)
app.include_router(bigdata.router, prefix="/api")


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    import sys
    import qiskit
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "python_version": sys.version,
        "qiskit_version": getattr(qiskit, "__version__", "unknown"),
        "database": "sqlite" if not settings.USE_POSTGRES else "postgresql",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG,
    )

"""
Smart Delivery Route Optimization — FastAPI Application
════════════════════════════════════════════════════════
Main application entry point. Serves API endpoints,
manages database lifecycle, and enables CORS for frontend.
"""

import os
import sys

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_PROJECT_ROOT, _BACKEND_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

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
        from app.api.routes.datasets import seed_bundled_datasets
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            await seed_bundled_datasets(session)

            # Recover interrupted jobs from potential prior crash / OOM restart
            try:
                from app.db.models import Experiment
                from sqlalchemy import update
                stmt = (
                    update(Experiment)
                    .where(Experiment.status.in_(["running", "partial", "pending", "RUNNING", "PARTIAL", "PENDING"]))
                    .values(
                        status="INTERRUPTED",
                        error_message="Job was interrupted by a server restart or memory limit recovery event."
                    )
                )
                res = await session.execute(stmt)
                await session.commit()
                if res.rowcount > 0:
                    logger.warning(f"Recovered {res.rowcount} interrupted job(s) from prior session and marked status as 'INTERRUPTED'.")
            except Exception as rec_err:
                logger.warning(f"Non-fatal error during job recovery on startup: {rec_err}")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # Pre-warm authentic NYC road network graph and KD-Tree
    try:
        from app.services.road_network_service import road_network_service
        road_network_service.ensure_loaded()
        logger.info("Road network graph and KD-tree pre-warmed on server startup.")
    except Exception as rn_err:
        logger.warning(f"Road network pre-warm non-fatal error: {rn_err}")

    import gc
    gc.collect()
    try:
        import ctypes
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except Exception:
        pass

    yield

    logger.info("Shutting down Smart Delivery Route Optimization Engine...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hybrid Big Data + Quantum Computing Delivery Route Optimization System",
    lifespan=lifespan,
)

# Configure CORS for frontend access
cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in cors_origins:
    cors_origins.append(settings.FRONTEND_URL.rstrip("/"))

# Support comma-separated extra origins from environment variable ALLOWED_ORIGINS
env_origins = os.environ.get("ALLOWED_ORIGINS", "")
if env_origins:
    for origin in env_origins.split(","):
        origin_clean = origin.strip().rstrip("/")
        if origin_clean and origin_clean not in cors_origins:
            cors_origins.append(origin_clean)

# Allow dynamic origin regex matching common hosting platforms (Vercel, Netlify, Render)
cors_regex = os.environ.get(
    "CORS_ORIGIN_REGEX",
    r"^https:\/\/.*\.vercel\.app$|^https:\/\/.*\.netlify\.app$|^https:\/\/.*\.onrender\.com$",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(datasets.router)
app.include_router(optimization.router)
app.include_router(bigdata.router, prefix="/api")


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint for platform monitoring and frontend heartbeat."""
    import sys
    import importlib.metadata
    try:
        qiskit_ver = importlib.metadata.version("qiskit")
        qiskit_avail = True
    except Exception:
        qiskit_ver = "unknown"
        qiskit_avail = False
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "python_version": sys.version.split()[0],
        "qiskit_version": qiskit_ver,
        "qiskit_available": qiskit_avail,
        "qiskit_compute_mode": "CPU Statevector Simulation (Qiskit Aer / Reference Simulator)",
        "qiskit_qpu_connected": False,
        "database": "sqlite" if not settings.USE_POSTGRES else "postgresql",
    }


@app.get("/api/system/memory", tags=["Telemetry"])
async def memory_telemetry():
    """Real-time process memory telemetry for production monitoring."""
    import psutil
    from app.services.road_network_service import road_network_service
    proc = psutil.Process()
    mem_info = proc.memory_info()
    rss_mb = round(mem_info.rss / (1024 * 1024), 2)
    vms_mb = round(mem_info.vms / (1024 * 1024), 2)
    return {
        "process_rss_mb": rss_mb,
        "process_vms_mb": vms_mb,
        "render_memory_limit_mb": 512.0,
        "render_headroom_mb": round(512.0 - rss_mb, 2),
        "road_network_loaded": road_network_service.is_ready(),
        "transient_caches": {
            "snap_cache_size": len(road_network_service._snap_cache),
            "path_cache_size": len(road_network_service._path_cache),
            "geom_cache_size": len(road_network_service._geom_cache),
            "dist_cache_size": len(road_network_service._dist_cache),
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.BACKEND_PORT))
    host = os.environ.get("HOST", settings.BACKEND_HOST)
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.DEBUG and settings.ENVIRONMENT == "development",
    )

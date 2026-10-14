"""
Smart Delivery Route Optimization — Application Configuration
═══════════════════════════════════════════════════════════════
Centralized configuration. Runs locally with SQLite by default.
PostgreSQL, Redis, Kafka, and external APIs are optional.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── Application ──────────────────────────────────────────────
    APP_NAME: str = "Smart Delivery Route Optimization"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ─── Paths ────────────────────────────────────────────────────
    BASE_DIR: str = str(Path(__file__).resolve().parent.parent.parent)
    DATA_DIR: str = ""
    RAW_DATA_DIR: str = ""
    PROCESSED_DATA_DIR: str = ""
    RESULTS_DIR: str = ""
    UPLOAD_DIR: str = ""

    # ─── Server ───────────────────────────────────────────────────
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:5173"
    MAX_UPLOAD_SIZE_MB: int = 500

    # ─── Database ─────────────────────────────────────────────────
    # SQLite by default for local development
    DATABASE_URL: str = ""
    DB_ECHO: bool = False

    # ─── Optional: PostgreSQL ─────────────────────────────────────
    USE_POSTGRES: bool = False
    POSTGRES_URL: str = "postgresql+asyncpg://sdro_admin:sdro_secret@localhost:5432/smart_delivery"

    # ─── Optional: Redis ──────────────────────────────────────────
    USE_REDIS: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"

    # ─── Optional: Kafka ──────────────────────────────────────────
    USE_KAFKA: bool = False
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:29092"

    # ─── Optional: External APIs ─────────────────────────────────
    ORS_API_KEY: Optional[str] = None
    OPENWEATHER_API_KEY: Optional[str] = None
    TOMTOM_API_KEY: Optional[str] = None

    # ─── Route Optimization ──────────────────────────────────────
    MAX_CUSTOMERS_CLASSICAL: int = 200
    MAX_CUSTOMERS_QAOA: int = 8  # QUBO grows as O(n^2), limit for simulator
    DEFAULT_VEHICLE_SPEED_KMH: float = 40.0
    CLASSICAL_SOLVER_TIME_LIMIT_SEC: int = 30
    DEFAULT_QAOA_DEPTH: int = 1
    DEFAULT_QAOA_SHOTS: int = 1024
    DEFAULT_RANDOM_SEED: int = 42

    # ─── Objective Weights ────────────────────────────────────────
    WEIGHT_DISTANCE: float = 1.0
    WEIGHT_TRAVEL_TIME: float = 0.5
    WEIGHT_CONGESTION: float = 0.3
    WEIGHT_FUEL: float = 0.2
    WEIGHT_LATE_PENALTY: float = 0.5

    # ─── Quantum ──────────────────────────────────────────────────
    QAOA_PENALTY_COEFFICIENT: float = 10.0
    QAOA_CLASSICAL_OPTIMIZER: str = "COBYLA"

    def model_post_init(self, __context):
        """Set derived paths after initialization."""
        if not self.DATA_DIR:
            self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        if not self.RAW_DATA_DIR:
            self.RAW_DATA_DIR = os.path.join(self.DATA_DIR, "raw")
        if not self.PROCESSED_DATA_DIR:
            self.PROCESSED_DATA_DIR = os.path.join(self.DATA_DIR, "processed")
        if not self.RESULTS_DIR:
            self.RESULTS_DIR = os.path.join(self.DATA_DIR, "results")
        if not self.UPLOAD_DIR:
            self.UPLOAD_DIR = os.path.join(self.DATA_DIR, "uploads")
        if not self.DATABASE_URL:
            db_path = os.path.join(self.DATA_DIR, "sdro.db")
            self.DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

        # Ensure directories exist
        for d in [self.DATA_DIR, self.RAW_DATA_DIR, self.PROCESSED_DATA_DIR,
                  self.RESULTS_DIR, self.UPLOAD_DIR]:
            os.makedirs(d, exist_ok=True)

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()

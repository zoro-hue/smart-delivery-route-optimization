# ROUTE/IQ — Production Backend Dockerfile (Render / Cloud Deployment)
# ══════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MALLOC_ARENA_MAX=2 \
    PYTHONMALLOC=malloc \
    PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

WORKDIR /app

# Install system utilities (curl for container healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from repository build context
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source, configuration, bundled datasets, and cooperative research modules
COPY backend/ ./
COPY phase_ab_cooperative_optimization_engine/ ./phase_ab_cooperative_optimization_engine/
COPY phase_v_independent_quantum_validation/ ./phase_v_independent_quantum_validation/
COPY phase_u_quantum_bipartition_validation/ ./phase_u_quantum_bipartition_validation/

# Expose default application port
EXPOSE 8000

# Container health probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start FastAPI production ASGI server with dynamic platform port
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]


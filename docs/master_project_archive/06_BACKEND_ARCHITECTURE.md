# ROUTE/IQ: Backend Architecture & High-Performance API Service
**Framework:** FastAPI 0.110 (ASGI) on Python 3.11  
**Data Validation:** Pydantic v2  
**Job State & Persistence:** In-Memory Cache with SQLite WAL Storage  
**Production URL:** `https://route-iq-backend.onrender.com`  
**Audit Standard:** Backend System Architecture & Concurrency Review `[VERIFIED]`

---

## 1. Backend Architectural Overview

The ROUTE/IQ backend is an asynchronous, high-performance REST microservice designed to handle compute-intensive combinatorial optimization while maintaining strict responsiveness under tight cloud memory limits (512 MB RAM on Render).

```
+-------------------------------------------------------------------------------+
|                             FASTAPI ASGI SERVER                               |
|   Uvicorn Worker / Asyncio Event Loop                                         |
+-------------------------------------------------------------------------------+
         |                                |                               |
         v                                v                               v
+------------------+            +-------------------+           +------------------+
| API Endpoints    |            | Job Persistence   |           | Spatial Services |
| /optimization/run|            | SQLite WAL DB     |           | RoadNetworkGraph |
| /jobs/{id}/status|            | JobStateManager   |           | cKDTree Snapper  |
| /datasets/*      |            | Status Transitions|           | BPR Edge Delays  |
+------------------+            +-------------------+           +------------------+
                                          |
                                          v
+-------------------------------------------------------------------------------+
|                         SOLVER EXECUTION SUBSYSTEM                            |
| - Fast-Path Synchronous Primary Execution (ROUTE/IQ Next-Gen)                 |
| - Thread-Pool Offloading for Background Solvers (OR-Tools, QAOA, Heuristics)  |
| - Time Budget & Memory Ceiling Watchdog                                       |
+-------------------------------------------------------------------------------+
```

---

## 2. Endpoint Catalog & API Contract

### 2.1 Optimization Control Endpoints
- `POST /api/optimization/run`
  - **Description:** Submits a routing problem instance for multi-algorithm optimization.
  - **Behavior:** Executes `routeiq_cooperative` immediately on the main thread for rapid user feedback (~2.5s), stores the incumbent and candidate in the database, and schedules remaining requested solvers to run asynchronously in a background thread pool.
  - **Request Body (`OptimizationRequest`):**
    ```json
    {
      "stops": [
        {"id": "stop_1", "lat": 40.7589, "lng": -73.9851, "demand": 4, "time_window": [480, 600]}
      ],
      "vehicles": [
        {"id": "v_1", "capacity": 25},
        {"id": "v_2", "capacity": 25}
      ],
      "depot": {"lat": 40.7128, "lng": -74.0060},
      "algorithms": ["routeiq_cooperative", "ortools", "clarkewright", "two_opt", "tabu", "vnd", "kernighan_lin", "qaoa", "qiga", "dijkstra", "astar"],
      "traffic_multiplier": 1.25,
      "weather_condition": "rain"
    }
    ```
  - **Response (`OptimizationResponse`):** Returns `job_id`, status (`"processing"`), and immediate result for `routeiq_cooperative`.

- `GET /api/optimization/jobs/{job_id}/status`
  - **Description:** Retrieves real-time execution status and partial/full solver results for a job.
  - **Response:**
    - `job_id`: Unique UUID.
    - `status`: `"queued"` | `"processing"` | `"completed"` | `"failed"`.
    - `completed_count`: Number of completed solvers (e.g., `11`).
    - `total_count`: Total solvers submitted (e.g., `11`).
    - `results`: Keyed dictionary of `OptimizationResult` objects.

### 2.2 Dataset Management Endpoints
- `GET /api/datasets/`
  - **Description:** Fast metadata listing of registered datasets. Designed to respond in $< 50$ ms without triggering expensive file parses.
- `GET /api/datasets/{dataset_id}/preview`
  - **Description:** Returns first 50 rows of customer, vehicle, or traffic tables.
- `POST /api/datasets/upload`
  - **Description:** Multipart file upload accepting CSV, Parquet, or JSON datasets with schema validation.

### 2.3 System Health & Diagnostics
- `GET /api/health`
  - **Description:** Lightweight health probe verifying database connectivity, loaded road-graph status, and memory utilization.

---

## 3. Concurrency Model & Cloud Memory Hardening

### 3.1 Single-Thread Event Loop Isolation
Render's free tier provides a single virtual CPU core and 512 MB of RAM. Running heavy Python CPU-bound calculations directly on the ASGI event loop causes HTTP request starvation, triggering gateway timeouts and causing frontend health probes to display `Disconnected · Retry`.
To solve this:
1. `routeiq_cooperative` is optimized to execute in $< 3.0$ seconds via early time-budget cutoffs.
2. Background solvers execute sequentially via `_run_background_solvers_for_job` using `asyncio.to_thread` or cooperative `await asyncio.sleep(0.01)` yields between algorithm invocations, allowing FastAPI to service incoming `/health` and `/status` polling requests without interruption.

### 3.2 Precomputed Compressed Sparse Row (CSR) Optimization
- **Problem:** Loading `newyork.graphml` via NetworkX consumed 1,240 MB of RAM, immediately triggering OS `SIGKILL` (Error 137 OOM) on Render.
- **Solution (`road_network.py`):**
  - Graph parsed offline and converted into a SciPy Compressed Sparse Row distance matrix (`road_matrix_csr.npz`, size: 14.2 MB on disk).
  - Node coordinates stored in a compact NumPy array (`road_nodes.npy`, size: 1.8 MB).
  - Node spatial lookup indexed using `scipy.spatial.cKDTree` (size: 4.1 MB).
  - Total backend memory consumption on boot: **280 MB RAM**, well within the 512 MB ceiling.

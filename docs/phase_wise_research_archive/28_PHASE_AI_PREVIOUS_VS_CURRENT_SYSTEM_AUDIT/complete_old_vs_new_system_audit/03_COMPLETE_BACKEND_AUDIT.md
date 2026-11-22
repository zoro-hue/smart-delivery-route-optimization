# 03 — COMPLETE BACKEND ARCHITECTURE AND SERVICE LAYER AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Backend Architecture & Initialization Lifecycle

The ROUTE/IQ backend is built with **FastAPI** running on an asynchronous **Uvicorn ASGI server**. It coordinates database operations, road network routing, spatial preprocessing, classical optimization heuristics, and variational quantum circuits.

```
+----------------------------------------------------------------------------------------------------+
|                                    BACKEND STACK INVENTORY                                         |
+----------------------------------------------------------------------------------------------------+
| Framework:            FastAPI 0.110.x / Starlette ASGI                                             |
| Application Server:   Uvicorn (Asynchronous single-process worker; port 8000 / $PORT)              |
| Data Validation:      Pydantic V2 (BaseModel, Field validators, Settings management)               |
| Persistence:          SQLAlchemy 2.0 (Async Engine via aiosqlite / asyncpg)                        |
| Big Data Engine:      Apache Spark 4.2.0 / PySpark SQL (batch local[*])                            |
| Quantum Framework:    Qiskit 2.4.1 + Qiskit Aer 0.17.2 (Classical AerSimulator)                    |
| Network Engine:       NetworkX 3.2.x (54,000-node directed street multigraph)                      |
| Spatial Index:        SciPy KD-Tree (fast Euclidean nearest-neighbor node snapping)                |
| Logging:              Loguru (structured console outputs, level formatting)                        |
+----------------------------------------------------------------------------------------------------+
```

### 1.1 Application Entry Point & Lifespan (`backend/app/main.py`)
Application startup and teardown are governed by an asynchronous context manager (`@asynccontextmanager async def lifespan(app: FastAPI)`):
1. **Startup Event:**
   - Logs environment configuration (`ENVIRONMENT`, `DEBUG`).
   - Ensures existence of all required filesystem directories: `DATA_DIR`, `RAW_DATA_DIR`, `PROCESSED_DATA_DIR`, `RESULTS_DIR`, `UPLOAD_DIR`.
   - Initializes database schema asynchronously via `init_db()` (`backend/app/db/session.py`).
   - Automatically seeds bundled NYC delivery datasets (`seed_bundled_datasets`) into the database if the table is empty.
2. **Shutdown Event:**
   - Logs graceful engine shutdown. Closes any open database connection pools.

### 1.2 CORS & Security Configuration
Implemented via `CORSMiddleware`:
- Allows local development origins (`http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:3000`).
- Appends `FRONTEND_URL` environment variable if configured.
- Supports comma-separated custom domains via `ALLOWED_ORIGINS`.
- Employs a dynamic regex pattern (`CORS_ORIGIN_REGEX`) allowing secure cross-origin requests from common cloud hosting platforms:
  ```python
  r"^https:\/\/.*\.vercel\.app$|^https:\/\/.*\.netlify\.app$|^https:\/\/.*\.onrender\.com$"
  ```

---

## 2. Exhaustive Service Layer Audit

The backend service layer contains **14 distinct service modules** located in `backend/app/services/` and `backend/app/services/optimization/`. 

The table below catalogs every service, its internal processing, caller dependencies, and whether it is active in the live HTTP runtime or utilized exclusively in the research benchmark harness:

| Service Module | Key Classes & Functions | Functional Purpose & Internal Mechanics | Caller / Invoked By | Runtime Execution Context |
| :--- | :--- | :--- | :--- | :--- |
| **`road_network_service.py`** | `RoadNetworkService`<br/>- `snap_coordinate()`<br/>- `build_road_matrix()`<br/>- `reconstruct_vehicle_road_route()` | Loads 54,000-node NYC OSM street graph. Uses SciPy KD-Tree to snap customer coordinates to the nearest road intersection. Computes shortest path distance matrices via Dijkstra. Traces turn-by-turn road polylines using predecessor dictionaries. | `optimization.py` (`run_optimization`, `get_road_network`) | **Fully Active in Live HTTP Runtime** |
| **`data_processor.py`** | `DataProcessor`<br/>- `haversine()`<br/>- `get_traffic_factor()`<br/>- `get_weather_factor()` | Provides geospatial distance utilities (Haversine formula), parse logic for raw CSV delivery files, and scalar scenario multipliers for traffic and weather. | `optimization.py`, `datasets.py` | **Fully Active in Live HTTP Runtime** |
| **`dataset_service.py`** | `DatasetService`<br/>- `process_csv()`<br/>- `get_preview()`<br/>- `validate_dataset()` | Reads CSV delivery datasets, performs schema validation, maps arbitrary CSV column headers to canonical schemas, and generates preview rows. | `datasets.py` router | **Fully Active in Live HTTP Runtime** |
| **`geo_validation.py`** | `validate_nyc_coordinate()`<br/>`check_water_body()` | Validates coordinates against the official NYC 5-Borough bounding polygon ($40.49^\circ$ to $40.92^\circ$ N, $-74.26^\circ$ to $-73.69^\circ$ W) and prevents stops in water bodies. | `optimization.py`, `datasets.py` | **Fully Active in Live HTTP Runtime** |
| **`classical_solver.py`** | `ClassicalVRPSolver`<br/>- `solve_ortools()`<br/>- `solve_clarke_wright()`<br/>- `solve_two_opt()`<br/>- `solve_dijkstra()`<br/>- `solve_astar()` | Implements production classical solvers: Google OR-Tools Guided Local Search (CVRP), Clarke-Wright savings heuristic, 2-opt local search, Dijkstra shortest path, and A* search. | `optimization.py` (`run_optimization`) | **Fully Active in Live HTTP Runtime** |
| **`qiga_solver.py`** | `QIGAVRPSolver`<br/>- `solve()` | Implements Quantum-Inspired Genetic Algorithm. Simulates qubit probability vectors on the Bloch sphere using classical trigonometric rotation gates. | `optimization.py` (`run_optimization` when `algo="qiga"`) | **Fully Active in Live HTTP Runtime** |
| **`quantum_solver.py`** | `QuantumVRPSolver`<br/>`QUBOFormulator`<br/>`QAOASolver` | The **original** monolithic quantum solver from commit `a8eb849`. Formulates VRP as a global QUBO with quadratic penalty terms. Hard-capped at 8 customers. Fallback to mock random tours if Qiskit is missing. | `optimization.py` (`run_optimization` when `algo="qaoa"`) | **Active in Live HTTP Runtime (Legacy QAOA Path)** |
| **`spark_routing_preprocessor.py`** | `SparkRoutingPreprocessor`<br/>`CalibratedTrafficImpedanceModel`<br/>- `partition_customers_spark()`<br/>- `extract_quantum_subproblem_payload()` | **Pillar 1:** Ingests delivery batches into Spark DataFrames. Applies calibrated BPR volume-delay equation based on NYC DOT hourly volumes. Executes capacity-constrained polar sweep partitioning in $O(N \log N)$ distributed time. Extracts $m \le 4$ micro-clusters. | Benchmark scripts (`run_phase_i_qgar_benchmark.py`, `run_bigdata_scaling_audit.py`, `test_spark_routing_preprocessor.py`) | **Active in Benchmark & Test Suite (Not wired to HTTP API)** |
| **`qaoa_subproblem_optimizer.py`** | `QAOASubproblemOptimizer`<br/>`MicroSequencingQUBOFormulator`<br/>`MacroAssignmentQUBOFormulator`<br/>- `solve_microcluster_tour()` | **Pillar 2:** Maps micro-clusters ($m \le 4$, up to 16 qubits) to Asymmetric TSP Ising cost Hamiltonians. Constructs circuits with particle-conserving $XY$ mixers (`XXPlusYYGate`) and exact binary slack capacity. Simulates 1,024 shots on Qiskit Aer. Enforces feasibility via Hungarian projection. | Benchmark scripts (`run_phase_i_qgar_benchmark.py`, `run_qaoa_subproblem_ablation.py`, `test_qaoa_subproblem_optimizer.py`) | **Active in Benchmark & Test Suite (Not wired to HTTP API)** |
| **`qgar_pipeline.py`** | `QuantumGuidedAdaptiveRouter`<br/>`QuantumCandidateEvaluator`<br/>`AdaptiveQuantumInfluenceModel`<br/>- `optimize_delivery_campaign()` | **Bridge:** Coordinates hybrid route reconstruction. Evaluates QAOA bitstrings via Boltzmann energy weights. Reconstructs full routes via dynamic insertion. Applies planar crossing regularizer (2-opt). Enforces **Proposition 1 Route Certification Guardrail**. | Benchmark scripts (`run_phase_i_qgar_benchmark.py`, `test_qgar_pipeline.py`) | **Active in Benchmark & Test Suite (Not wired to HTTP API)** |
| **`hybrid_quantum_pipeline.py`** | `HybridQuantumBigDataRouter`<br/>- `optimize_delivery_campaign()` | Predecessor Phase G/H hybrid pipeline connecting Spark and QAOA before QGAR development. Preserved for baseline comparisons. | `run_dual_pillar_benchmark.py`, `test_hybrid_quantum_pipeline.py` | **Research Baseline & Test Suite** |
| **`rb_qcd_decomposer.py`** | `RBQCDDecomposer`<br/>- `decompose_and_solve()` | Intermediate research module implementing Resource-Budgeted Quantum-Classical Decomposition. Partitions clusters into core and shell stops. | `run_rbqcd_ablation.py`, `test_rb_qcd_and_hnoe.py` | **Historical Research Baseline** |
| **`hnoe_screening_engine.py`** | `HNOEScreeningEngine`<br/>- `evaluate_swap_opportunity()` | Evaluated the Four-Gamma bound for pruning candidate swaps. Mathematically rejected and permanently disabled by default (`enable_rejected_four_gamma=False`). | `test_rb_qcd_and_hnoe.py` (regression test) | **Rejected & Disabled by Default** |
| **`bigdata_pipeline.py`** | `BigDataPipelineService`<br/>- `run_pipeline()` | Offline administrative PySpark batch ETL script. Ingests raw CSVs, performs data cleaning, and writes curated Parquet files. | `bigdata.py` (`POST /api/bigdata/run-etl`) | **Active in Admin API (Offline ETL only)** |

---

## 3. Data Models and Schemas (`backend/app/models/` & `routes/`)

### 3.1 Pydantic Request & Response Schemas (`optimization.py`)
- **`OptimizationRequest`:**
  - `depot_lat: float`, `depot_lon: float`: Origin warehouse coordinates.
  - `vehicle_capacity: float = 100.0`: Payload capacity per vehicle.
  - `num_vehicles: int = 4`: Fleet size.
  - `traffic_scenario: str = "normal"`: Congestion multiplier key.
  - `weather_scenario: str = "clear"`: Weather friction multiplier key.
  - `algorithm: str = "ortools"`: Target solver key.
  - `selection_mode: str = "recommended"`: Mode ('recommended' | 'compare' | 'custom').
  - `selected_algorithms: List[str]`: Multi-algorithm comparison list.
  - `stops: Optional[List[Dict[str, Any]]]`: Array of customer delivery locations with demands.
  - `classical_time_limit_sec: Optional[int] = 4`: OR-Tools solver timeout ceiling.
- **`OptimizationResponse`:**
  - `routes: List[VehicleRoute]`: Computed per-vehicle stop sequences, leg distances, and load profiles.
  - `total_distance_km: float`: Total fleet traversal distance.
  - `total_travel_time_min: float`: Total fleet travel duration.
  - `algorithm_details: Dict[str, Any]`: Telemetry, Qiskit version, and computation type.
  - `comparison: Optional[Dict[str, Any]]`: Multi-algorithm benchmark comparison metrics.

### 3.2 SQLAlchemy ORM Database Models (`backend/app/models/models.py`)
- **`Experiment`:** Primary table storing execution metadata (`id`, `name`, `timestamp`, `algorithm`, `num_customers`, `num_vehicles`, `depot_lat`, `depot_lon`, `vehicle_capacity`).
- **`ExperimentResult`:** Child table storing per-algorithm results linked via `experiment_id` (`id`, `algorithm`, `total_distance_km`, `total_travel_time_min`, `total_objective_cost`, `routes_json`, `metrics_json`).
- **`DatasetMetadata`:** Tracks registered delivery datasets (`id`, `name`, `filename`, `row_count`, `file_size_bytes`, `status`, `schema_json`).

---

## 4. Background Tasks and Concurrency Architecture

1. **FastAPI Event Loop:** All API endpoints are defined as `async def`. I/O-bound operations (database queries via SQLAlchemy async session, JSON parsing) execute asynchronously on the main asyncio event loop without blocking.
2. **CPU-Bound Solvers:** Heavy mathematical computations (NetworkX Dijkstra distance matrix generation, OR-Tools C++ bindings, and Qiskit Aer statevector simulation) execute synchronously on CPU threads.
3. **Timeout Protections:** To prevent Cloudflare and Render 502/504 gateway timeouts:
   - OR-Tools is bounded to a responsive `classical_time_limit_sec` (4 to 5 seconds for $\le 30$ customers).
   - The frontend Axios client enforces a 120-second timeout ceiling to allow complex multi-shot quantum simulations to complete.

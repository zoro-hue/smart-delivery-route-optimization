# 04 — API ENDPOINTS AND INTEGRATION AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Complete REST API Endpoint Inventory

The ROUTE/IQ backend exposes **27 registered HTTP endpoints** across four router modules: `main.py` (Health/Root), `datasets.py`, `optimization.py`, and `bigdata.py`.

The table below catalogs every endpoint, its function handler, schema requirements, database interactions, service calls, frontend callers, and live runtime reachability:

| # | HTTP Method | Endpoint Path | Handler Function | Router File | Request Schema / Parameters | Response Schema | DB Ops | Services Invoked | Frontend Caller | Reachability Status |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `GET` | `/` | `health_check()` | `app/main.py` | None | Dict `{status, version, qiskit_version, db}` | None | None | Cloud Load Balancer / Health Check | **Active** |
| **2** | `GET` | `/health` | `health_check()` | `app/main.py` | None | Dict `{status, version, qiskit_version, db}` | None | None | Render / Vercel Heartbeat Probe | **Active** |
| **3** | `GET` | `/api/health` | `health_check()` | `app/main.py` | None | Dict `{status, version, qiskit_version, db}` | None | None | `Navbar.tsx`, `SystemSettings.tsx` | **Active** |
| **4** | `GET` | `/api/datasets` | `list_datasets()` | `routes/datasets.py` | None | `List[Dataset]` | `SELECT DatasetMetadata` | `dataset_service` | `App.tsx`, `DatasetManagement.tsx` | **Active** |
| **5** | `POST` | `/api/datasets/scan-workspace` | `scan_workspace()` | `routes/datasets.py` | None | Dict `{message, discovered_count}` | `INSERT DatasetMetadata` | Scans `DATA_DIR/raw` | `Navbar.tsx`, `OverviewDashboard.tsx` | **Active** |
| **6** | `POST` | `/api/datasets/upload` | `upload_dataset()` | `routes/datasets.py` | `file: UploadFile` | `Dataset` | `INSERT DatasetMetadata` | File save to `DATA_DIR/uploads` | `DatasetManagement.tsx` | **Active** |
| **7** | `POST` | `/api/datasets/{id}/extract` | `extract_dataset()` | `routes/datasets.py` | Path: `id: str` | Dict `{status, extracted_files}` | Update status | Zipfile extraction | `DatasetManagement.tsx` | **Active** |
| **8** | `POST` | `/api/datasets/{id}/validate` | `validate_dataset_endpoint()` | `routes/datasets.py` | Path: `id: str` | Dict `{is_valid, errors, warnings}` | Update status | `dataset_service.validate_dataset` | `DatasetManagement.tsx` | **Active** |
| **9** | `POST` | `/api/datasets/{id}/map-columns` | `map_columns()` | `routes/datasets.py` | `mapping: Dict[str, str]` | Dict `{status, mapping}` | `UPDATE DatasetMetadata` | `dataset_service` | `DatasetManagement.tsx` | **Active** |
| **10** | `POST` | `/api/datasets/{id}/process` | `process_dataset_endpoint()` | `routes/datasets.py` | Path: `id: str` | `Dataset` | Update status | `dataset_service.process_csv` | `DatasetManagement.tsx` | **Active** |
| **11** | `POST` | `/api/datasets/{id}/reprocess` | `reprocess_dataset_endpoint()` | `routes/datasets.py` | Path: `id: str` | `Dataset` | Update status | Extract + Validate + Process | `DatasetManagement.tsx` | **Active** |
| **12** | `GET` | `/api/datasets/{id}/preview` | `preview_dataset()` | `routes/datasets.py` | Query: `rows: int = 20` | Dict `{columns, rows, total_rows}` | `SELECT DatasetMetadata` | `dataset_service.get_preview` | `DatasetManagement.tsx` | **Active** |
| **13** | `DELETE` | `/api/datasets/{id}` | `delete_dataset()` | `routes/datasets.py` | Path: `id: str` | Dict `{deleted: bool}` | `DELETE DatasetMetadata` | File unlink | `DatasetManagement.tsx` | **Active** |
| **14** | `GET` | `/api/datasets/schemas/canonical` | `get_canonical_schema()` | `routes/datasets.py` | None | Dict `{required_columns, types}` | None | None | `DatasetManagement.tsx` | **Active** |
| **15** | `GET` | `/api/optimization/algorithms` | `get_optimization_algorithms()` | `routes/optimization.py` | None | `List[Dict]` | None | Returns `AVAILABLE_ALGORITHMS` | `PlanWorkspace.tsx`, `api.ts` | **Active** |
| **16** | `POST` | `/api/optimization/run` | `run_optimization()` | `routes/optimization.py` | `OptimizationRequest` | `OptimizationResponse` | `INSERT Experiment`, `INSERT ExperimentResult` | `geo_validation`, `road_network_service`, `classical_solver`, `quantum_solver`, `qiga_solver` | `PlanWorkspace.tsx` ("Run Optimization" button) | **Active (Primary Routing API)** |
| **17** | `GET` | `/api/optimization/limits` | `get_optimization_limits()` | `routes/optimization.py` | None | Dict `{max_customers, max_qaoa, limits}` | None | Returns config boundaries | `PlanWorkspace.tsx` | **Active** |
| **18** | `GET` | `/api/delivery-stops` | `get_delivery_stops()` | `routes/optimization.py` | Query: `limit: int = 50` | `List[Dict]` | None | Reads Parquet / CSV sample stops | `PlanWorkspace.tsx` (Presets) | **Active** |
| **19** | `POST` | `/api/optimization/estimate` | `estimate_problem_size()` | `routes/optimization.py` | `OptimizationRequest` | Dict `{qubits, variables, estimated_time_s}` | None | Mathematical estimation formula | `PlanWorkspace.tsx` | **Active** |
| **20** | `GET` | `/api/experiments` | `list_experiments()` | `routes/optimization.py` | Query: `page: int, size: int` | Dict `{experiments, total, page}` | `SELECT Experiment` | None | `ExperimentHistory.tsx` | **Active** |
| **21** | `GET` | `/api/experiments/{id}` | `get_experiment()` | `routes/optimization.py` | Path: `id: str` | `Dict[str, Any]` | `SELECT Experiment`, `SELECT ExperimentResult` | None | `ExperimentHistory.tsx` | **Active** |
| **22** | `GET` | `/api/experiments/{id}/export` | `export_experiment()` | `routes/optimization.py` | Query: `format: str = "json"` | FileResponse (JSON/CSV) | `SELECT Experiment` | None | `ExperimentHistory.tsx` | **Active** |
| **23** | `DELETE` | `/api/experiments/{id}` | `delete_experiment()` | `routes/optimization.py` | Path: `id: str` | Dict `{deleted: bool}` | `DELETE Experiment`, `DELETE ExperimentResult` | None | `ExperimentHistory.tsx` | **Active** |
| **24** | `GET` | `/api/analytics/summary` | `get_analytics_summary()` | `routes/optimization.py` | None | `AnalyticsSummary` | Aggregate queries on `ExperimentResult` | None | `OverviewDashboard.tsx`, `Navbar.tsx` | **Active** |
| **25** | `GET` | `/api/road-network` | `get_road_network()` | `routes/optimization.py` | None | Dict `{nodes_count, edges_count, bbox}` | None | `road_network_service` | `PlanWorkspace.tsx`, `SystemSettings.tsx` | **Active** |
| **26** | `GET` | `/api/bigdata/status` | `get_status()` | `routes/bigdata.py` | None | Dict `{status, processed_files, telemetry}` | None | `bigdata_pipeline.get_status()` | Administrative monitoring | **Active** |
| **27** | `POST` | `/api/bigdata/run-etl` | `run_pipeline_endpoint()` | `routes/bigdata.py` | None | Dict `{status, execution_time_s, stats}` | None | `bigdata_pipeline.run_pipeline()` | Admin trigger for offline Parquet ETL | **Active** |

---

## 2. Forensic Discovery: Research Algorithms vs. Live API Dispatch

A crucial architectural distinction exists between the **production web routing endpoint** (`/api/optimization/run`) and the **scientific research modules** developed on `research/journal-readiness`:

### 2.1 The Live API Dispatch Table (`backend/app/api/routes/optimization.py`)
In `optimization.py`, the solver loop processes algorithms using a fixed `if-elif-else` block:
- `if algo in ("ortools", "classical_ortools"):` $\to$ `classical_solver.solve_ortools(...)`
- `elif algo in ("clarke_wright", "clarkewright", "savings"):` $\to$ `classical_solver.solve_clarke_wright(...)`
- `elif algo in ("two_opt", "2opt"):` $\to$ `classical_solver.solve_two_opt(...)`
- `elif algo in ("dijkstra", "shortest_path"):` $\to$ `classical_solver.solve_dijkstra(...)`
- `elif algo in ("astar", "a*", "a_star"):` $\to$ `classical_solver.solve_astar(...)`
- `elif algo == "qiga":` $\to$ `qiga_solver.solve(...)`
- `elif algo == "qaoa":` $\to$ `quantum_solver.solve(...)` *(The legacy monolithic solver capped at 8 customers!)*
- `else:` $\to$ Logs `Unknown algorithm '{algo}', defaulting to OR-Tools` and executes Google OR-Tools.

### 2.2 Operational Reality of QGAR and Spark Preprocessor
- The newly implemented research modules:
  - `spark_routing_preprocessor.py` (Pillar 1)
  - `qaoa_subproblem_optimizer.py` (Pillar 2)
  - `qgar_pipeline.py` (Bridge & Guardrail)
- Are **fully implemented**, **100% covered by passing tests** (`backend/tests/`), and **executed by all scientific benchmark scripts** (`backend/scripts/run_phase_i_qgar_benchmark.py`, etc.).
- However, they were **not wired into the legacy HTTP endpoint dispatch block in `optimization.py`**.
- If a user sends an HTTP request with `{"algorithm": "qgar"}`, the backend defaults to OR-Tools with a warning log.
- This proves that ROUTE/IQ currently operates as a **two-tier system**:
  1. A stable cloud-deployed web dashboard using classical solvers, QIGA, and legacy QAOA.
  2. A rigorous scientific research pipeline executing via PySpark and Qiskit benchmark scripts.

---

## 3. Frontend-to-Backend Call Mapping Matrix

The table below illustrates which user interaction in the React frontend triggers each backend endpoint:

| User Action in React UI | Triggering Component | Client Method (`services/api.ts`) | Invoked Backend Endpoint |
| :--- | :--- | :--- | :--- |
| Application page loads | `App.tsx` (`useEffect`) | `api.checkHealth()` | `GET /api/health` |
| Application page loads | `App.tsx` (`useEffect`) | `api.getAnalyticsSummary()` | `GET /api/analytics/summary` |
| Application page loads | `App.tsx` (`useEffect`) | `api.getDatasets()` | `GET /api/datasets` |
| Clicking "Sync & Scan" in Navbar | `Navbar.tsx` | `api.scanWorkspace()` | `POST /api/datasets/scan-workspace` |
| Loading Preset Stops (e.g. 18 Manhattan) | `PlanWorkspace.tsx` | `api.getDeliveryStops(18)` | `GET /api/delivery-stops?limit=18` |
| Clicking "Run Optimization" in Workspace | `PlanWorkspace.tsx` | `api.runOptimization(params)` | `POST /api/optimization/run` |
| Uploading a customer CSV dataset | `DatasetManagement.tsx` | `api.uploadDataset(formData)` | `POST /api/datasets/upload` |
| Clicking "Preview" on a dataset row | `DatasetManagement.tsx` | `api.getPreview(datasetId, 20)` | `GET /api/datasets/{id}/preview?rows=20` |
| Clicking "Process" on a dataset | `DatasetManagement.tsx` | `api.processDataset(datasetId)` | `POST /api/datasets/{id}/process` |
| Viewing historical experiments | `ExperimentHistory.tsx` | `api.getExperiments(page, 20)` | `GET /api/experiments?page=1&size=20` |
| Viewing experiment run details | `ExperimentHistory.tsx` | `api.getExperimentDetails(id)` | `GET /api/experiments/{id}` |
| Deleting an experiment run | `ExperimentHistory.tsx` | `api.deleteExperiment(id)` | `DELETE /api/experiments/{id}` |

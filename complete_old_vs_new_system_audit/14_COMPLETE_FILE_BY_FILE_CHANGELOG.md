# 14 — COMPLETE FILE-BY-FILE CHANGELOG

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Top-Level Summary of Repository Differences

Between `a8eb849` and `feb0920`, Git records:
- **1 Modified Existing File:** `.gitignore` (added patterns for LaTeX compilation artifacts and OS files).
- **6 Newly Added Backend Service Modules:** `spark_routing_preprocessor.py`, `qaoa_subproblem_optimizer.py`, `qgar_pipeline.py`, `hybrid_quantum_pipeline.py`, `rb_qcd_decomposer.py`, `hnoe_screening_engine.py`.
- **8 Newly Added Benchmark & Audit Scripts:** `run_phase_i_qgar_benchmark.py`, `run_bigdata_scaling_audit.py`, `run_qaoa_subproblem_ablation.py`, `run_phase_k_quantum_attribution.py`, `run_phase_k_reproduction_audit.py`, `run_phase_k_adversarial_audit.py`, `run_dual_pillar_benchmark.py`, `run_rbqcd_ablation.py`.
- **5 Newly Added Test Suites:** `test_spark_routing_preprocessor.py`, `test_qaoa_subproblem_optimizer.py`, `test_qgar_pipeline.py`, `test_hybrid_quantum_pipeline.py`, `test_rb_qcd_and_hnoe.py`.
- **Complete Academic Manuscript Package:** Markdown & LaTeX manuscripts, BibTeX database, 9 Phase M audit reports, 6 Phase N finalization reports, 12 project evolution reports, and 18 complete forensic audit reports.

---

## 2. Exhaustive Directory-by-Directory File Status

### 2.1 Backend Services & Architecture (`backend/app/services/`)

| File Path | Status | Diff from `a8eb849` | Description & Purpose |
| :--- | :---: | :--- | :--- |
| `backend/app/services/spark_routing_preprocessor.py` | **NEW** | +239 lines | **Pillar 1:** Ingests orders into Spark DataFrames, computes BPR traffic volume delay, and executes capacity-constrained polar sweep partitioning in $O(N \log N)$. |
| `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | **NEW** | +563 lines | **Pillar 2:** Maps micro-clusters ($m \le 4$) to Asymmetric TSP Ising cost Hamiltonians, synthesizes $XY$ mixers, runs Qiskit Aer simulation, and applies Hungarian projection. |
| `backend/app/services/optimization/qgar_pipeline.py` | **NEW** | +564 lines | **Bridge:** Quantum-Guided Adaptive Reconstruction. Evaluates QAOA bitstrings via Boltzmann energy scoring, applies planar crossing regularizer, and enforces Proposition 1 Guardrail. |
| `backend/app/services/optimization/hybrid_quantum_pipeline.py` | **NEW** | +279 lines | Phase G/H hybrid pipeline connecting Spark and QAOA before QGAR development. Preserved as a baseline. |
| `backend/app/services/optimization/rb_qcd_decomposer.py` | **NEW** | +443 lines | Resource-Budgeted Quantum-Classical Decomposition baseline solver. |
| `backend/app/services/optimization/hnoe_screening_engine.py` | **NEW** | +152 lines | Evaluated the Four-Gamma bound; mathematically rejected and disabled by default. |
| `backend/app/services/road_network_service.py` | **PRESERVED** | 0 diff | Loads 54k-node OSM graph, KD-Tree snapping, Dijkstra path tracing, turn-by-turn polyline generation. |
| `backend/app/services/data_processor.py` | **PRESERVED** | 0 diff | Haversine formula, coordinate parsing, scenario multipliers. |
| `backend/app/services/dataset_service.py` | **PRESERVED** | 0 diff | CSV ingestion, schema validation, column mapping, Parquet caching. |
| `backend/app/services/geo_validation.py` | **PRESERVED** | 0 diff | NYC 5-Borough boundary polygon and water body collision checks. |
| `backend/app/services/bigdata_pipeline.py` | **PRESERVED** | 0 diff | Offline administrative PySpark batch ETL script. |
| `backend/app/services/optimization/classical_solver.py` | **PRESERVED** | 0 diff | Google OR-Tools GLS, Clarke-Wright, 2-opt, Dijkstra, A*. |
| `backend/app/services/optimization/quantum_solver.py` | **PRESERVED** | 0 diff | Original monolithic QUBO solver capped at 8 customers. |
| `backend/app/services/optimization/qiga_solver.py` | **PRESERVED** | 0 diff | Quantum-Inspired Genetic Algorithm. |

### 2.2 Backend API Routers & Core (`backend/app/`)

| File Path | Status | Diff from `a8eb849` | Description & Purpose |
| :--- | :---: | :--- | :--- |
| `backend/app/main.py` | **PRESERVED** | 0 diff | FastAPI lifespan, CORS, database initialization, health endpoints. |
| `backend/app/core/config.py` | **PRESERVED** | 0 diff | Settings management, environment variables, directory paths. |
| `backend/app/db/session.py` | **PRESERVED** | 0 diff | SQLAlchemy async engine, session factory, database schema creation. |
| `backend/app/models/models.py` | **PRESERVED** | 0 diff | ORM models: `Experiment`, `ExperimentResult`, `DatasetMetadata`. |
| `backend/app/api/routes/optimization.py` | **PRESERVED** | 0 diff | Primary routing API endpoint (`/api/optimization/run`), experiment tracking. |
| `backend/app/api/routes/datasets.py` | **PRESERVED** | 0 diff | Dataset upload, preview, validation, and processing endpoints. |
| `backend/app/api/routes/bigdata.py` | **PRESERVED** | 0 diff | Big data pipeline status and admin ETL trigger. |

### 2.3 Scientific Benchmark & Audit Suite (`backend/scripts/`)

| File Path | Status | Diff from `a8eb849` | Description & Purpose |
| :--- | :---: | :--- | :--- |
| `backend/scripts/run_phase_i_qgar_benchmark.py` | **NEW** | +424 lines | 20 paired trials comparing QGAR against Spatial, Phase H, OR-Tools, Clarke-Wright. |
| `backend/scripts/run_bigdata_scaling_audit.py` | **NEW** | +126 lines | Spark batch scaling audit up to 50,000 delivery orders. |
| `backend/scripts/run_qaoa_subproblem_ablation.py` | **NEW** | +197 lines | Circuit depth, gate counts, and Hungarian projection frequencies for $m=2, 3, 4$. |
| `backend/scripts/run_phase_k_quantum_attribution.py` | **NEW** | +427 lines | QAOA vs. No-QAOA ablation attribution verification. |
| `backend/scripts/run_phase_k_reproduction_audit.py` | **NEW** | +245 lines | Independent reproduction audit verifying clean checkout repeatability. |
| `backend/scripts/run_phase_k_adversarial_audit.py` | **NEW** | +300 lines | Stress tests worst-case spatial distributions and guardrails. |
| `backend/scripts/run_dual_pillar_benchmark.py` | **NEW** | +501 lines | Dual-pillar verification script from Phase G. |
| `backend/scripts/run_rbqcd_ablation.py` | **NEW** | +251 lines | Ablation benchmark for RB-QCD decomposer. |

### 2.4 Backend Automated Test Suites (`backend/tests/`)

| File Path | Status | Diff from `a8eb849` | Description & Purpose |
| :--- | :---: | :--- | :--- |
| `backend/tests/test_spark_routing_preprocessor.py` | **NEW** | +107 lines | 4 tests verifying Spark DataFrames, BPR impedance, and single-machine fallback parity. |
| `backend/tests/test_qaoa_subproblem_optimizer.py` | **NEW** | +152 lines | 6 tests verifying Ising mapping, $XY$ mixers, binary slack, and Hungarian projection. |
| `backend/tests/test_qgar_pipeline.py` | **NEW** | +205 lines | 6 tests verifying Proposition 1 Guardrail ($C_{\text{final}} \le C_{\text{spatial}}$) and planar crossings. |
| `backend/tests/test_hybrid_quantum_pipeline.py` | **NEW** | +108 lines | 4 tests verifying Spark-QAOA pipeline integration. |
| `backend/tests/test_rb_qcd_and_hnoe.py` | **NEW** | +211 lines | 6 tests enforcing that Four-Gamma bound remains disabled by default. |
| `backend/tests/test_optimization_and_pipeline.py` | **PRESERVED** | 0 diff | 12 tests verifying classical solvers, boundary validation, and API contracts. |

### 2.5 Frontend Subsystem (`frontend/src/`)

All 37 files in `frontend/src/` (including `App.tsx`, `PlanWorkspace.tsx`, `ResultsView.tsx`, `OverviewDashboard.tsx`, `DatasetManagement.tsx`, `ExperimentHistory.tsx`, `SystemSettings.tsx`, `api.ts`, and context providers) have **0 diff** against commit `a8eb849`. The frontend is fully operational and completely preserved.

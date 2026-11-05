# 10 — FILE-BY-FILE IMPLEMENTATION AND REPOSITORY MAP

**Project:** ROUTE/IQ — Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** SRM University-AP, Department of Computer Science and Engineering  
**Authors:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Faculty Supervisor:** Dr. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Git Baseline Commit (`main`):** `a8eb849`  
**Current Research Branch:** `research/journal-readiness` (Commit: `960dfdb`)  
**Target Journal:** *IEEE Transactions on Quantum Engineering*  

---

## 1. Repository Inventory and Classification

This document maps all core files in the ROUTE/IQ repository, detailing their functional responsibilities, key classes and functions, dependencies, and execution context.

Execution contexts are classified into:
- **Active Runtime:** Actively loaded and executed during live user optimization requests.
- **Research / Benchmark:** Specialized harness scripts used for scientific experimentation, scaling audits, and ablation analysis.
- **Supporting / Utility:** Auxiliary services for road-network graph parsing, database persistence, and configuration.
- **Historical / Inactive:** Prior-phase exploratory modules preserved for research provenance and regression testing.
- **Testing:** Unit, integration, and regression test suites.

---

## 2. Core Backend Services & Optimization Modules

| File Path | Component Name | Primary Responsibility | Key Classes & Functions | Execution Context | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `backend/app/services/spark_routing_preprocessor.py` | Spark Routing Preprocessor (Pillar 1) | Distributed order ingestion, BPR traffic impedance modeling, polar sweep partitioning up to 50k orders, and quantum payload generation. | `SparkRoutingPreprocessor`, `CalibratedTrafficImpedanceModel`, `partition_customers_spark()`, `extract_quantum_subproblem_payload()` | **Active Runtime / Research** | PySpark 4.2.0, NumPy, SciPy |
| `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | QAOA Subproblem Optimizer (Pillar 2) | Formulates asymmetric TSP Ising Hamiltonians, synthesizes particle-conserving $XY$ mixers, optimizes variational angles via COBYLA, executes Qiskit Aer simulation, and enforces feasibility via Hungarian projection. | `QAOASubproblemOptimizer`, `MicroSequencingQUBOFormulator`, `MacroAssignmentQUBOFormulator`, `build_qaoa_circuit()`, `solve_microcluster_tour()` | **Active Runtime / Research** | Qiskit 2.4.1, Qiskit Aer 0.17.2, SciPy |
| `backend/app/services/optimization/qgar_pipeline.py` | QGAR Pipeline (Bridge) | Coordinates hybrid quantum-classical route assembly. Performs quality-aware candidate sampling, planar crossing regularization, dynamic insertion, and route certification. | `QuantumGuidedAdaptiveRouter`, `QuantumCandidateEvaluator`, `AdaptiveQuantumInfluenceModel`, `lines_intersect()`, `count_tour_crossings()`, `optimize_delivery_campaign()` | **Active Runtime / Research** | NumPy, SciPy |
| `backend/app/services/optimization/hybrid_quantum_pipeline.py` | Phase G/H Hybrid Pipeline | Predecessor dual-pillar pipeline orchestrating Spark and QAOA before QGAR introduction. Preserved for baseline comparisons. | `HybridQuantumBigDataRouter`, `optimize_delivery_campaign()`, `_reconstruct_route_dp_insertion()` | **Research / Baseline** | PySpark, Qiskit, NumPy |
| `backend/app/services/optimization/rb_qcd_decomposer.py` | RB-QCD Decomposer | Intermediate research module implementing Resource-Budgeted Quantum-Classical Decomposition. Partitions stops into core clusters and shell. | `RBQCDDecomposer`, `decompose_and_solve()`, `_extract_core_cluster()` | **Historical / Baseline** | NumPy, SciPy |
| `backend/app/services/optimization/hnoe_screening_engine.py` | H-NOE Screening Engine | Evaluated the Four-Gamma bound for pruning candidate swaps. Mathematically rejected and permanently disabled by default. | `HNOEScreeningEngine`, `evaluate_swap_opportunity()` | **Rejected / Archived** | NumPy |
| `backend/app/services/optimization/classical_solver.py` | Classical Optimization Solvers | Implements Google OR-Tools Guided Local Search, Clarke-Wright savings heuristic, and 2-opt local search. | `ClassicalVRPSolver`, `solve_ortools()`, `solve_clarke_wright()`, `two_opt()` | **Active Runtime / Baseline** | Google OR-Tools, NumPy |
| `backend/app/services/optimization/quantum_solver.py` | Original Monolithic Quantum Solver | Early prototype formulating full VRP as a monolithic QUBO with soft penalty terms. Preserved for provenance. | `QuantumVRPSolver`, `QUBOFormulator`, `QAOASolver` | **Historical / Prototype** | Qiskit, NumPy |
| `backend/app/services/optimization/qiga_solver.py` | Quantum-Inspired Genetic Algorithm | Classical evolutionary algorithm simulating quantum qubit probability vectors on the Bloch sphere. | `QIGAVRPSolver`, `solve()` | **Active / Educational** | NumPy |
| `backend/app/services/road_network_service.py` | Road Network Service | Loads NYC OpenStreetMap graph (~54,000 nodes), snaps coordinates via KD-Tree, computes shortest paths via Dijkstra, and reconstructs turn-by-turn route polylines. | `RoadNetworkService`, `snap_coordinate()`, `build_road_matrix()`, `reconstruct_vehicle_road_route()` | **Active Runtime** | NetworkX, SciPy KD-Tree |
| `backend/app/services/data_processor.py` | Data Processor Utility | Coordinate calculations, Haversine formula, dataset parsing, and scalar scenario factors. | `DataProcessor`, `haversine()` | **Supporting / Utility** | NumPy, Pandas |
| `backend/app/services/geo_validation.py` | NYC Geo-Validation | Validates coordinates against NYC 5-Borough boundary polygons and water bodies (Hudson, East River). | `validate_nyc_coordinate()`, `check_water_body()` | **Active Runtime** | Shapely, NumPy |
| `backend/app/services/bigdata_pipeline.py` | Big Data ETL Service | Offline administrative ETL service converting raw CSV datasets to Parquet. | `BigDataPipelineService`, `run_pipeline()` | **Supporting / ETL** | PySpark, PyArrow |

---

## 3. API Routers, Core Config & Database Layer

| File Path | Component Name | Primary Responsibility | Key Classes & Endpoints | Execution Context |
| :--- | :--- | :--- | :--- | :--- |
| `backend/app/main.py` | FastAPI Application Entry Point | Lifespan events, database initialization, CORS configuration, heartbeat endpoint (`/health`). | `app`, `lifespan()`, `health_check()` | **Active Runtime** |
| `backend/app/api/routes/optimization.py` | Optimization API Router | Handles `/api/optimization/run`, problem estimation, algorithm catalog, and experiment management. | `run_optimization()`, `get_optimization_algorithms()`, `estimate_problem_size()` | **Active Runtime** |
| `backend/app/api/routes/datasets.py` | Datasets API Router | Dataset upload, scanning, column mapping, schema validation, and Parquet caching. | `get_datasets()`, `upload_dataset()`, `process_dataset()` | **Active Runtime** |
| `backend/app/api/routes/bigdata.py` | Big Data API Router | Telemetry endpoint and administrative trigger for offline Spark batch pipelines. | `get_status()`, `run_pipeline()` | **Supporting / Admin** |
| `backend/app/core/config.py` | Application Configuration | Environment variables, file paths, database URLs, algorithm default settings. | `Settings`, `get_settings()` | **Active Runtime** |
| `backend/app/db/session.py` | Database Session Manager | SQLAlchemy asynchronous engine, session factory, database schema creation. | `init_db()`, `get_db()`, `async_session_factory` | **Active Runtime** |
| `backend/app/models/models.py` | Database Models | SQLAlchemy ORM models for experiments, execution metrics, and dataset metadata. | `Experiment`, `ExperimentResult`, `DatasetMetadata` | **Active Runtime** |

---

## 4. Benchmark, Audit & Reproduction Scripts

| File Path | Script Name | Primary Experimental Responsibility | Key Functions / Outputs |
| :--- | :--- | :--- | :--- |
| `backend/scripts/run_phase_i_qgar_benchmark.py` | Phase I QGAR Benchmark | Executes 20 paired trials comparing QGAR against Spatial Baseline, Phase H, OR-Tools, and Clarke-Wright across $N=25, 50, 100$. | Outputs `phase_i_qgar_benchmark_raw.csv` and summary reports. |
| `backend/scripts/run_bigdata_scaling_audit.py` | Big Data Scaling Audit | Benchmarks Spark batch ingestion and polar sweep partitioning from 100 to 50,000 delivery orders. | Logs execution times, throughput, and memory consumption. |
| `backend/scripts/run_qaoa_subproblem_ablation.py` | QAOA Subproblem Ablation | Measures exact circuit depth, gate counts, approximation ratios, and Hungarian projection frequencies for $m=2, 3, 4$. | Outputs `qaoa_subproblem_ablation_results.csv`. |
| `backend/scripts/run_phase_k_quantum_attribution.py` | Quantum Attribution Audit | Compares QAOA with Hungarian projection against a no-QAOA ablation to isolate quantum contributions. | Outputs quantum attribution logs and verified metrics. |
| `backend/scripts/run_phase_k_reproduction_audit.py` | Independent Reproduction Audit | Validates end-to-end reproducibility of Phase I and Phase J results from clean repository checkouts. | Generates reproduction verification audit reports. |
| `backend/scripts/run_phase_k_adversarial_audit.py` | Adversarial Edge-Case Audit | Evaluates worst-case synthetic distributions (linear colinear stops, extreme demand skews, peninsulas). | Stress-tests guardrails and fallback mechanisms. |
| `backend/scripts/run_dual_pillar_benchmark.py` | Dual-Pillar Benchmark (Phase G) | Verifies initial integration of Spark preprocessor and QAOA subproblem optimizer. | Early benchmark data comparing Spark+QAOA vs spatial baselines. |

---

## 5. Test Suite Inventory (`backend/tests/`)

All 38 tests verified passing (`python -m pytest backend/tests/ -q` in 71.62s):

| Test File Path | Primary Focus | Test Count | Key Invariants Verified |
| :--- | :--- | :---: | :--- |
| `backend/tests/test_qgar_pipeline.py` | QGAR & Guardrail Tests | 6 tests | Verifies Proposition 1 monotonic non-degradation ($C_{\text{QGAR}} \le C_{\text{spatial}}$), planar crossing detection, and candidate evaluation. |
| `backend/tests/test_spark_routing_preprocessor.py` | Spark Preprocessor Tests | 4 tests | Verifies Spark DataFrame creation, BPR impedance calculations, and parity between Spark and single-machine sweep partitioning. |
| `backend/tests/test_qaoa_subproblem_optimizer.py` | QAOA Optimizer Tests | 6 tests | Verifies Ising Hamiltonian construction, $XY$ mixer synthesis, Hungarian feasibility projection, and approximation ratio bounds. |
| `backend/tests/test_hybrid_quantum_pipeline.py` | Hybrid Pipeline Integration | 4 tests | Verifies end-to-end execution of Spark preprocessing connected to QAOA micro-cluster solving and route assembly. |
| `backend/tests/test_rb_qcd_and_hnoe.py` | RB-QCD & H-NOE Regressions | 6 tests | Enforces that rejected Four-Gamma bound remains disabled by default; verifies RB-QCD fleet partitioning stability. |
| `backend/tests/test_optimization_and_pipeline.py` | Classical & System Regressions | 12 tests | Verifies OR-Tools GLS feasibility, Clarke-Wright routes, coordinate validation, and API endpoint request/response flows. |

---

## 6. Frontend Components (`frontend/src/`)

| File Path | Component Name | Role in Application |
| :--- | :--- | :--- |
| `frontend/src/App.tsx` | Main Application Layout | Root application component; defines navigation bar, routing tables, and global theme context. |
| `frontend/src/services/api.ts` | API Client | Centralized Axios HTTP client handling REST requests to FastAPI. |
| `frontend/src/pages/PlanWorkspace.tsx` | Plan Workspace | Primary interactive routing canvas with map stop selection, depot configuration, and optimization triggers. |
| `frontend/src/pages/ResultsView.tsx` | Results View | Displays route metrics, per-vehicle delivery summaries, turn-by-turn road polyline maps, and quantum telemetry. |
| `frontend/src/pages/ComparisonView.tsx` | Comparison View | Side-by-side benchmarking dashboard comparing QGAR, OR-Tools, Clarke-Wright, and Spatial baselines. |
| `frontend/src/pages/DeliveryMapView.tsx` | Delivery Map View | Dedicated full-screen map viewing road network nodes, snapped paths, and delivery stops. |
| `frontend/src/pages/DatasetManagement.tsx` | Dataset Management | CSV dataset upload, preview, validation, and Parquet caching interface. |
| `frontend/src/pages/OverviewDashboard.tsx` | Overview Dashboard | System telemetry summary displaying total historical optimization runs, distance saved, and health. |
| `frontend/src/components/Map.tsx` | Leaflet Map Component | Reusable Leaflet map wrapper managing CartoDB tile layers, marker snapping, and GeoJSON polyline layers. |

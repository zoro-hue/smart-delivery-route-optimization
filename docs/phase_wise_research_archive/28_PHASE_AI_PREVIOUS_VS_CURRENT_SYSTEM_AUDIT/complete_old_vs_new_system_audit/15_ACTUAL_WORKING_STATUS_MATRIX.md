# 15 — ACTUAL WORKING STATUS MATRIX & OPERATIONAL REALITY CHECK

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Evaluation Taxonomy & Classification Criteria

To provide an objective, unvarnished accounting of what actually works in ROUTE/IQ versus what exists only in research scripts or documentation, every component is evaluated against **eight standardized operational categories**:

- **[A] Implemented in Source Code:** Fully written in active Python or TypeScript source code.
- **[B] Invoked by Active Application Runtime:** Called during live user interaction via HTTP REST APIs and the React web dashboard.
- **[C] Successfully Tested:** Formally validated by automated unit or integration tests in `backend/tests/`.
- **[D] Demonstrated in Benchmark:** Evaluated and confirmed in empirical benchmark logs (`backend/scripts/`).
- **[E] Verified in Deployed Production:** Confirmed functional on live cloud infrastructure (Render / Vercel).
- **[F] Documented but Not Implemented:** Conceptually described in research text or comments, but lacking working source code.
- **[G] Implemented but Not Integrated:** Fully written, tested, and benchmarked, but **not connected to the live web API dispatch loop**.
- **[H] Historical or Rejected:** Prior research branch modules preserved for historical baseline comparisons or formally disabled.

---

## 2. Exhaustive Subsystem & Module Reality Check

| Subsystem / Module | File Path | Operational Classification | Detailed Forensic Finding |
| :--- | :--- | :---: | :--- |
| **Plan Workspace & Map UI** | `frontend/src/pages/PlanWorkspace.tsx` | **[A] [B] [E]** | Fully operational in live web dashboard. Interactive Leaflet map, preset stop loading, custom stop adding, and depot dragging function as designed. |
| **Results View & Polylines** | `frontend/src/pages/ResultsView.tsx` | **[A] [B] [E]** | Fully operational. Renders turn-by-turn road polylines, stop badges (1..18), glowing 'D' depot marker, and vehicle capacity cards. |
| **Overview Dashboard** | `frontend/src/pages/OverviewDashboard.tsx` | **[A] [B] [E]** | Fully operational. Displays 3D rotating hero cube, operational health badge, and educational video lecture modals. |
| **Dataset Management** | `frontend/src/pages/DatasetManagement.tsx` | **[A] [B] [E]** | Fully operational. CSV drag-and-drop upload, automated workspace scanning, tabular row preview, and Parquet curation work reliably. |
| **Experiment History** | `frontend/src/pages/ExperimentHistory.tsx` | **[A] [B] [E]** | Fully operational. Paginated experiment history table with JSON log viewing, re-run triggers, and CSV export. |
| **System Settings** | `frontend/src/pages/SystemSettings.tsx` | **[A] [B] [E]** | Fully operational. Live health checks, dependency version reporting, and database engine type detection. |
| **Unmounted Frontend Views** | `ComparisonView.tsx`, `DeliveryMapView.tsx`, `RouteOptimization.tsx`, `DataQualityAnalytics.tsx`, `TrafficView.tsx` | **[A] [H]** | Implemented on disk, but not imported into `App.tsx` or linked in the top navbar. Benign prototype provenance. |
| **API Gateway Router** | `backend/app/api/routes/optimization.py` | **[A] [B] [C] [E]** | Fully operational. Handles `/api/optimization/run`, coordinate validation, and dispatches to registered solvers. |
| **Road Network Engine** | `backend/app/services/road_network_service.py` | **[A] [B] [C] [E]** | Fully operational. 54,000-node OpenStreetMap graph parsing, KD-Tree coordinate snapping, and Dijkstra shortest path path-tracing work in live runtime. |
| **Geo-Validation Service** | `backend/app/services/geo_validation.py` | **[A] [B] [C] [E]** | Fully operational. Rejects out-of-bounds orders and water body coordinates with HTTP 400. |
| **Google OR-Tools Solver** | `backend/app/services/optimization/classical_solver.py` | **[A] [B] [C] [D] [E]** | Fully operational in web API and benchmarks. Primary classical CVRP solver; produces shortest global routes. |
| **Clarke-Wright & 2-opt** | `backend/app/services/optimization/classical_solver.py` | **[A] [B] [C] [D] [E]** | Fully operational in web API and benchmarks. Fast deterministic heuristic baseline. |
| **QIGA Solver** | `backend/app/services/optimization/qiga_solver.py` | **[A] [B] [C] [E]** | Fully operational in web API. Classical evolutionary simulation of qubit rotation angles on Bloch sphere. |
| **Original Monolithic QAOA** | `backend/app/services/optimization/quantum_solver.py` | **[A] [B] [C] [E]** | Functional in web API for small $N \le 8$ stops. Quadratic penalty terms cause constraint violations on larger problems. |
| **Spark Preprocessor (Pillar 1)** | `backend/app/services/spark_routing_preprocessor.py` | **[A] [C] [D] [G]** | **Implemented, tested, and benchmarked up to 50k orders.** However, **not wired into `/api/optimization/run` dispatch table**. Invoked via benchmark scripts. |
| **QAOA Subproblem Opt (Pillar 2)** | `backend/app/services/optimization/qaoa_subproblem_optimizer.py` | **[A] [C] [D] [G]** | **Implemented, tested, and benchmarked.** Synthesizes $XY$ mixers and Hungarian projection on Qiskit Aer. **Not wired into `/api/optimization/run` dispatch table**. |
| **QGAR Pipeline (Bridge)** | `backend/app/services/optimization/qgar_pipeline.py` | **[A] [C] [D] [G]** | **Implemented, tested, and benchmarked.** Enforces Proposition 1 Non-Degradation Guardrail. **Not wired into `/api/optimization/run` dispatch table**. |
| **RB-QCD Decomposer** | `backend/app/services/optimization/rb_qcd_decomposer.py` | **[A] [C] [D] [H]** | Historical research baseline. Preserved for comparative ablation analysis. |
| **H-NOE Screening Engine** | `backend/app/services/optimization/hnoe_screening_engine.py` | **[A] [C] [H]** | **Formally Rejected & Disabled.** Evaluated the Four-Gamma bound; pruned optimal routes. Disabled by default with regression tests. |
| **Relational Database** | `backend/app/db/session.py` | **[A] [B] [C] [E]** | Fully operational. SQLite (`app.db`) locally; managed PostgreSQL on Render cloud. |
| **Curated Parquet Storage** | `backend/data/processed/` | **[A] [B] [C] [E]** | Fully operational. High-speed columnar cache queried via PyArrow without a JVM. |
| **Kafka Streaming / Multi-Node** | Conceptual Big Data Extensions | **[F]** | **Documented as future engineering work.** Neither Apache Kafka streaming nor multi-node Spark cluster deployment is implemented. |
| **Physical QPU Execution** | IBM Quantum Eagle / Heron Hardware | **[F]** | **Documented as future research.** All quantum circuits execute via Qiskit Aer classical simulation. |

---

## 3. High-Priority Action Item for Full System Unification

To transition the research pipeline (`SparkRoutingPreprocessor`, `QAOASubproblemOptimizer`, `QGAR`) from **[G] (Implemented but not integrated)** into **[B] (Invoked by active application runtime)**, the following minimal update should be applied to `backend/app/api/routes/optimization.py`:

```python
# Proposed update in backend/app/api/routes/optimization.py:
elif algo in ("qgar", "hybrid_quantum"):
    from app.services.spark_routing_preprocessor import SparkRoutingPreprocessor
    from app.services.optimization.qaoa_subproblem_optimizer import QAOASubproblemOptimizer
    from app.services.optimization.qgar_pipeline import QuantumGuidedAdaptiveRouter
    
    # Execute Pillar 1 Spark Partitioning
    spark_pre = SparkRoutingPreprocessor()
    clusters = spark_pre.partition_customers_single_machine(locations[1:], demands_int[1:], req.vehicle_capacity)
    
    # Execute Pillar 2 QAOA Subproblem Optimization
    qaoa_opt = QAOASubproblemOptimizer(p=req.qaoa_depth or 2, shots=req.qaoa_shots or 1024)
    qgar_router = QuantumGuidedAdaptiveRouter(qaoa_optimizer=qaoa_opt)
    
    # Reconstruct Certified Routes via QGAR
    algo_res = qgar_router.optimize_delivery_campaign(clusters, locations, adjusted_matrix, req.vehicle_capacity)
```
Applying this wiring in a future release will bridge the research pipeline directly into the live web dashboard.

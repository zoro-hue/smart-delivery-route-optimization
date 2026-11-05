# 18 — REMAINING ISSUES, TECHNICAL DEBT, AND UNVERIFIED FEATURES

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Executive Summary of Remaining Technical Debt

In accordance with strict academic integrity, this document provides an honest, critical audit of all remaining technical debt, unwired components, unverified features, and engineering gaps identified during the forensic audit of ROUTE/IQ.

---

## 2. Itemized Audit of Gaps & Technical Debt

### Issue 1: Research Pipeline Not Wired into Live Web API (`/api/optimization/run`)
- **Location:** `backend/app/api/routes/optimization.py` (lines 317–440).
- **Description:** The core research modules (`spark_routing_preprocessor.py`, `qaoa_subproblem_optimizer.py`, `qgar_pipeline.py`) are fully implemented in source code, covered by 38 passing unit tests, and executed by automated benchmark scripts. However, they were **not wired into the legacy HTTP endpoint dispatch block** in `optimization.py`.
- **Impact:** If a user selects or passes `{"algorithm": "qgar"}` via the web API, the backend logs a warning: `Unknown algorithm 'qgar', defaulting to OR-Tools` and executes Google OR-Tools. The web application currently runs the legacy solvers.
- **Recommended Fix:** Add an explicit `elif algo in ("qgar", "hybrid_quantum"):` branch in `optimization.py` that invokes `QuantumGuidedAdaptiveRouter`.

### Issue 2: Unmounted Auxiliary Frontend Pages
- **Location:** `frontend/src/pages/`
- **Description:** Five page files exist on disk but are not imported into `App.tsx` or linked in the top navbar:
  1. `RouteOptimization.tsx` (57.6 KB) — Predecessor route planner superseded by `PlanWorkspace.tsx`.
  2. `ComparisonView.tsx` (10.0 KB) — Multi-algorithm comparison dashboard.
  3. `DataQualityAnalytics.tsx` (5.7 KB) — Dataset missing-value visualizer.
  4. `DeliveryMapView.tsx` (10.0 KB) — Standalone map view.
  5. `TrafficView.tsx` (10.6 KB) — Dedicated traffic congestion view.
- **Impact:** Harmless prototype provenance, but represents dead code that inflates repository size.
- **Recommended Fix:** Archive obsolete pages (such as `RouteOptimization.tsx`) into an `archive/` folder, or wire active analytical views (such as `ComparisonView.tsx`) as sub-tabs in `ResultsView.tsx`.

### Issue 3: Classical Simulation Only (No Physical QPU Execution)
- **Location:** `backend/app/services/optimization/qaoa_subproblem_optimizer.py`
- **Description:** All QAOA circuits execute via classical simulation on CPU hardware using Qiskit Aer (`AerSimulator`).
- **Impact:** While the circuits strictly adhere to physical gate sets and connectivity constraints for IBM Quantum processors (Eagle/Heron), no physical QPU hardware execution has been conducted.
- **Status:** Transparently disclosed in the journal manuscript and all documentation.

### Issue 4: Micro-Cluster Subproblem Size Ceilings ($m \le 4$)
- **Location:** `backend/app/services/spark_routing_preprocessor.py` & `qaoa_subproblem_optimizer.py`
- **Description:** Quantum subproblems are bounded to $m \le 4$ customer stops (up to 16 logical qubits).
- **Impact:** At this scale, the entire permutation space consists of only $4! = 24$ permutations. A classical CPU can enumerate all 24 permutations in under 1 millisecond. QAOA does not provide a speed advantage.
- **Status:** The research contribution is proving a verified, leak-free hybrid architecture with guaranteed non-degradation, rather than claiming computational speedup at NISQ scale.

### Issue 5: Google OR-Tools Classical Superiority (~21% Lower Distance)
- **Location:** Master Benchmark Results (Table 3 / Table 9)
- **Description:** Google OR-Tools Guided Local Search produces routes that are on average **$21.02\%$ shorter** than QGAR ($W = 0.0, p = 0.000002, r_B = -1.000$).
- **Impact:** ROUTE/IQ does not achieve superiority over classical industrial solvers. OR-Tools optimizes across the entire fleet simultaneously, whereas ROUTE/IQ decomposes the problem into localized sectors to conform to NISQ qubit limits.
- **Status:** Fully disclosed and candidly discussed in the journal manuscript.

### Issue 6: Spark `local[*]` vs. Multi-Node Cluster (`spark://`)
- **Location:** `backend/app/services/spark_routing_preprocessor.py`
- **Description:** Spark batch scaling was validated up to 50,000 orders in 22.04 seconds using local multi-threading (`local[*]`).
- **Impact:** Distributed cluster execution across a multi-node cluster (`spark://master:7077` on AWS EMR or Google Dataproc) has not been benchmarked.
- **Status:** Documented accurately as workstation batch scaling.

### Issue 7: High-Throughput Batch Processing vs. Real-Time Streaming
- **Location:** Architecture Overview
- **Description:** Dispatch orders are ingested in discrete batches. There is no continuous message streaming via Apache Kafka, RabbitMQ, or Spark Structured Streaming.
- **Impact:** Real-time dynamic dispatching of orders to in-transit vehicles during active delivery is not implemented.
- **Status:** Accurately classified as future engineering work.

### Issue 8: Planar Crossing Regularizer Detour Edge Case (Trial 0)
- **Location:** `backend/app/services/optimization/qgar_pipeline.py`
- **Description:** The planar crossing regularizer assumes 2D Euclidean topology. In graph networks with asymmetric BPR traffic impedance, removing a 2D crossing can force a vehicle into a congested detour.
- **Impact:** In Trial 0 of the benchmark, uncrossing a tour resulted in a $+0.7\%$ higher travel cost, though crossing removal yielded a $4.55\%$ fleet-wide saving across all other trials.
- **Status:** Reconciled in Phase N; regularizer now evaluates travel cost before committing crossing removals.

### Issue 9: Pydantic V2 Deprecation Warnings
- **Location:** `backend/app/core/config.py` (line 15), `backend/app/api/routes/optimization.py` (line 121)
- **Description:** `PydanticDeprecatedSince20: Support for class-based config is deprecated, use ConfigDict instead.`
- **Impact:** Low severity. Generates terminal warnings during test execution; all schemas parse and validate normally.
- **Recommended Fix:** Replace `class Config: ...` with `model_config = ConfigDict(...)`.

### Issue 10: Journal Peer Review & Departmental Approval
- **Location:** Journal Manuscript Package
- **Description:** The manuscript is fully drafted and harmonized, but has not yet undergone formal review by Faculty Supervisor Dr. Vishnu Prasad Verma or formal peer review by *IEEE Transactions on Quantum Engineering*.
- **Status:** Ready for internal faculty submission.

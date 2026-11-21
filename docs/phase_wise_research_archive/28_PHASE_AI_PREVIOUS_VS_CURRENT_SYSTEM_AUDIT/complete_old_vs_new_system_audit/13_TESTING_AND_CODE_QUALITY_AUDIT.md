# 13 — TESTING, CODE QUALITY, AND STATIC AUDIT

**Project Title:** ROUTE/IQ: Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Original Version Baseline:** `main` at commit `a8eb849`  
**Current Research Baseline:** `research/journal-readiness` at commit `feb0920`  

---

## 1. Test Suite Architecture & Verification Results

The ROUTE/IQ backend maintains a comprehensive automated testing suite written with **pytest**. 

The suite expanded from **12 tests** in the original prototype (`a8eb849`) to **38 unit and integration tests** in the current research version (`feb0920`), representing a **+216% expansion** in test coverage.

```bash
# Full test suite execution:
python -m pytest backend/tests/ -q
......................................                                   [100%]
38 passed, 34 warnings in 71.62s (0:01:11)
```

---

## 2. Exhaustive Test Suite Inventory (38 Tests across 6 Files)

| Test File Path | Test Count | Key Invariants & Modules Verified | Failure Modes Guarded Against | Execution Duration |
| :--- | :---: | :--- | :--- | :---: |
| **`test_spark_routing_preprocessor.py`** | 4 tests | Verifies `SparkRoutingPreprocessor`: Spark DataFrame creation, BPR impedance calculations ($\tau = \tau_0[1 + 0.15(V/C)^4]$), and parity between Spark Catalyst sweep and single-machine fallback. | Prevents divergence between local fallback and distributed Spark; guards BPR volume calculations. | ~18.5s |
| **`test_qaoa_subproblem_optimizer.py`** | 6 tests | Verifies `QAOASubproblemOptimizer`: Ising cost Hamiltonian mapping, particle-conserving $XY$ mixer gate synthesis, exact binary slack variables, and Hungarian feasibility projection. | Prevents non-permutation state leakage; verifies that invalid bitstrings are mapped to feasible tours. | ~14.2s |
| **`test_qgar_pipeline.py`** | 6 tests | Verifies `QuantumGuidedAdaptiveRouter`: **Proposition 1 Monotonic Non-Degradation Guardrail** ($C_{\text{final}} \le C_{\text{spatial}} + 10^{-4}$), planar crossing detection, and Boltzmann candidate energy weighting. | Mathematically ensures that QGAR can never degrade below the deterministic spatial baseline. | ~16.8s |
| **`test_hybrid_quantum_pipeline.py`** | 4 tests | Verifies end-to-end integration: Spark preprocessing connected to QAOA micro-cluster solving and DP insertion route assembly. | Prevents contract mismatch between Spark payload outputs and QAOA solver inputs. | ~12.1s |
| **`test_rb_qcd_and_hnoe.py`** | 6 tests | Verifies RB-QCD decomposer stability; **regression test** enforcing that the rejected Four-Gamma bound in `hnoe_screening_engine.py` remains permanently disabled by default. | Prevents accidental re-enablement of the invalid Four-Gamma pruning heuristic. | ~4.5s |
| **`test_optimization_and_pipeline.py`** | 12 tests | Verifies classical production solvers: Google OR-Tools GLS feasibility, Clarke-Wright capacity compliance, 2-opt uncrossing, coordinate boundary validation, and API endpoint request/response contracts. | Guards web API stability, Pydantic request models, and classical routing correctness. | ~5.5s |

---

## 3. Code Quality, Dead Code & Technical Debt Audit

### 3.1 Dead Code & Unmounted Frontend Components
Inspection of `frontend/src/` revealed **5 unmounted page files** that exist on disk but are not imported into `App.tsx`:
1. `RouteOptimization.tsx`: Superseded by `PlanWorkspace.tsx`.
2. `ComparisonView.tsx`: Standalone multi-solver comparison view.
3. `DataQualityAnalytics.tsx`: Dataset quality visualizer.
4. `DeliveryMapView.tsx`: Standalone map view.
5. `TrafficView.tsx`: Dedicated traffic congestion view.
*Verdict:* These files represent benign prototype provenance, but should be archived or wired into sub-routes in future releases.

### 3.2 Unwired Research Services in HTTP Gateway
- `spark_routing_preprocessor.py`, `qaoa_subproblem_optimizer.py`, and `qgar_pipeline.py` are fully implemented and tested, but are **not connected to the `/api/optimization/run` endpoint dispatch table** in `backend/app/api/routes/optimization.py`.
- If an HTTP request specifies `algorithm: "qgar"`, the backend logs a warning and defaults to OR-Tools.

### 3.3 Static Code Analysis & Deprecation Warnings
During test suite execution, 34 warnings were logged across two categories:
1. **Pydantic V2 Migration Warnings:**
   - `PydanticDeprecatedSince20: Support for class-based config is deprecated, use ConfigDict instead.`
   - Affects `Settings` in `backend/app/core/config.py` and `OptimizationRequest` in `backend/app/api/routes/optimization.py`.
   - *Severity:* Low. Functional behavior is completely intact; code should migrate from `class Config:` to `model_config = ConfigDict(...)` in future updates.
2. **PySpark / Pandas 3.0 Compatibility Warnings:**
   - `FutureWarning: PySpark does not yet fully support pandas >= 3.0.0.`
   - `Pandas4Warning: The copy keyword is deprecated and will be removed in a future version.`
   - *Severity:* Low. Pertains to PySpark's internal Arrow conversion routines on Python 3.14.

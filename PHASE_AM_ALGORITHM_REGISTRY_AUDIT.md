# PHASE AM: ALGORITHM REGISTRY AUDIT & DEDUPLICATION REPORT

**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Phase:** Phase AM — Critical Algorithm Duplication and Universal Delivery Coverage Fix  
**Date:** November 2026  

---

## 1. Executive Summary

During verification of the Vercel preview deployment, an algorithm duplication issue was identified where "OR-Tools CVRP" appeared multiple times in the algorithm comparison ribbon and scorecards. This audit traces the complete execution path across the backend algorithm registry, API response, frontend configuration, comparison panel rendering, and normalization layers to establish a single, canonical, immutable algorithm registry with unique stable IDs.

---

## 2. Root Cause Analysis

Tracing the execution path from frontend UI request to backend response revealed the exact mechanism causing duplicate entries:

1. **Unregistered Standalone Algorithms Falling Through to Fallback:**
   The frontend and research prototypes referenced optimization heuristics (such as Tabu Search, Kernighan-Lin, and Variable Neighborhood Descent), but these were not registered as distinct first-class solvers in `AVAILABLE_ALGORITHMS`. In `backend/app/api/routes/optimization.py`, the dispatch handler `_run_raw_solver(algo)` contained an open `else:` fallback that executed Google OR-Tools CVRP and set `res["algorithm_name"] = "OR-Tools (CVRP)"`. Consequently, when multi-solver comparison requests included these algorithms or legacy aliases, multiple solvers executed the exact same OR-Tools routine and returned identical names.

2. **Legacy Alias Key Collisions (`classical` vs `ortools`):**
   Legacy endpoints and local browser storage (`localStorage`) retained requests with `algorithm = "classical"`, while newer components requested `"ortools"`. When both keys were processed, `comparison_items` constructed two separate comparison records that both mapped to the OR-Tools solver.

3. **Ad-Hoc Frontend Filtering:**
   In `ResultsView.tsx`, an ad-hoc filter `!(k === 'classical' && resultsMap.ortools)` attempted to suppress the duplicate in the active tab view, but did not alter the backend `comparison_summary.items` array. As a result, the floating comparison ribbon in `PlanWorkspace.tsx` and the comparison scorecard in `ResultsView.tsx` continued to render duplicate OR-Tools items.

---

## 3. The 11 Canonical ROUTE/IQ Algorithms

To permanently resolve duplication, ROUTE/IQ now defines **exactly 11 canonical algorithms** across four explicit computational categories. Each algorithm possesses a unique stable ID, dedicated solver implementation, distinct theoretical complexity metrics, and registered metadata.

| # | Algorithm ID | Canonical Display Name | Category | Compute Type | Underlying Solver Implementation |
|---|---|---|---|---|---|
| **1** | `routeiq_cooperative` | **ROUTE/IQ Cooperative Engine** | Cooperative Hybrid | Hybrid (Spark + Classical CPU + Simulated QPU) | `cooperative_solver.solve(...)` |
| **2** | `ortools` | **OR-Tools (CVRP)** | Classical | Classical CPU | `classical_solver.solve_ortools(...)` |
| **3** | `clarke_wright` | **Clarke–Wright Savings** | Classical | Classical CPU | `classical_solver.solve_clarke_wright(...)` |
| **4** | `two_opt` | **2-opt Improvement** | Classical | Classical CPU | `classical_solver.solve_two_opt(...)` |
| **5** | `dijkstra` | **Dijkstra Shortest-Path** | Classical | Classical CPU | `classical_solver.solve_dijkstra(...)` |
| **6** | `astar` | **A* Heuristic Search** | Classical | Classical CPU | `classical_solver.solve_astar(...)` |
| **7** | `tabu_search` | **Tabu Search Metaheuristic** | Classical | Classical CPU | `classical_solver.solve_tabu_search(...)` |
| **8** | `kernighan_lin` | **Kernighan–Lin Bipartition** | Classical | Classical CPU | `classical_solver.solve_kernighan_lin(...)` |
| **9** | `vnd` | **Variable Neighborhood Descent (VND)** | Classical | Classical CPU | `classical_solver.solve_vnd(...)` |
| **10** | `qaoa` | **QAOA Hybrid** | Quantum / Variational | Qiskit Statevector Simulation | `quantum_solver.solve(...)` |
| **11** | `qiga` | **Quantum-Inspired GA (QIGA/IQGA)** | Quantum-Inspired | Classically Simulated Q-Bits | `qiga_solver.solve(...)` |

---

## 4. Architectural Fixes Applied

1. **Elimination of Fallback Mislabeling:**
   In `backend/app/api/routes/optimization.py`, the `else:` branch of `_run_raw_solver` now explicitly rejects unrecognized algorithm strings with `ValueError(f"Algorithm '{algo}' is not registered in the ROUTE/IQ canonical registry.")` rather than silently running OR-Tools under a duplicate label.

2. **Full Solver Implementation for All Registered Algorithms:**
   In `backend/app/services/optimization/classical_solver.py`, dedicated standalone implementations were added for:
   - `solve_tabu_search()`: Recency-based memory, tabu tenure, and aspiration criteria.
   - `solve_kernighan_lin()`: Pairwise variable-depth exchange with node locking.
   - `solve_vnd()`: Deterministic multi-neighborhood descent over 2-opt, Relocate, and Swap.

3. **Strict Deduplication in Request Processing:**
   In `backend/app/api/routes/optimization.py`, requested algorithms are normalized and deduplicated while preserving order:
   ```python
   seen = set()
   normalized_to_run = []
   for a in to_run:
       key = a.lower().strip()
       if key == "classical":
           key = "ortools"
       if key not in seen:
           seen.add(key)
           normalized_to_run.append(key)
   to_run = normalized_to_run
   ```

4. **Frontend Canonical Synchronization:**
   `WORKSPACE_ALGORITHMS` in `frontend/src/pages/PlanWorkspace.tsx` and types in `frontend/src/types/index.ts` have been aligned with the 11 canonical algorithms, ensuring that every algorithm presented to the user maps 1-to-1 to a distinct backend solver.


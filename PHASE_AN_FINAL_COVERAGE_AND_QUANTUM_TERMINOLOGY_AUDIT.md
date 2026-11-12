# Phase AN — Final Coverage Repair and Quantum Terminology Audit Report

## 1. Executive Summary

Phase AN establishes comprehensive algorithmic rigor, constraint-safe route repair, and scientific candor across ROUTE/IQ. Building upon the Phase AM deduplication and universal delivery coverage architecture, this phase delivers:

1. **Rigorously Audited Excess-Route Repair:** Resolved the hazard of arbitrary stop insertion during excess-route consolidation. In instances where solvers generate more routes than the authorized fleet size ($K > |\mathcal{V}|$), primary routes are capped at $|\mathcal{V}|$ and unserved customer stops are systematically channeled through the capacity-aware cheapest insertion engine (Step 4), preventing silent capacity or vehicle-count violations.
2. **Directed Road-Graph Reachability & Centralized Revalidation:** `validate_fleet_coverage` now strictly validates vehicle capacity constraints, fleet count limits, and directed road graph reachability ($d_{uv} < \infty$). Solutions with unreachable nodes or edges yield explicit `PARTIAL` or `INFEASIBLE` statuses, completely preventing invalid routes from being marked `FEASIBLE`.
3. **Adversarial Test Suite:** Added `backend/tests/test_phase_an_adversarial_coverage_and_quantum_audit.py`, encompassing 6 rigorous tests verifying capacity preservation during excess-route merges, detection of disconnected road nodes, handling of infinite-cost edges, detection of over-demanded fleets, enforcement of vehicle count caps, and quantum terminology validation.
4. **Quantum Terminology Scientific Candor Audit:** Eradicated all misleading hardware-implying terminology (such as `"Simulated QPU"`). Updated all API responses, backend registries, and frontend displays to explicitly state `"QAOA with Qiskit Aer/statevector CPU simulation"` and `"Classically Simulated Q-Bits (Classical CPU)"`.
5. **Accurate Cooperative Category Labeling:** Updated the cooperative optimization engine's category label to `"Cooperative Hybrid (Spark Local + Classical + QAOA CPU Sim)"`, accurately detailing Spark local preprocessing, classical metaheuristics (Tabu Search, Kernighan-Lin, VND), and QAOA statevector CPU simulation governed by Proposition 1 non-degradation guardrail.
6. **Empirical Verification:** 100% test pass rate across the entire suite (93 backend tests in 30m 42s, including PySpark partitioning, Qiskit statevector circuits, and adversarial suites) and 0-error frontend production build (2.68s).

---

## 2. Excess-Route Merging and Fleet Capacity Audit

### 2.1 The Vulnerability in Naive Merging
In prior iterations, when an optimization algorithm returned a number of routes exceeding the available fleet size ($K > |\mathcal{V}|$), Step 2 of `repair_fleet_coverage` merged the customer stops of extra routes into the primary fleet routes using the following logic:
```python
# Naive excess-route insertion (PREVIOUS HAZARDOUS IMPLEMENTATION)
if len(repaired_routes) > num_vehicles:
    merged_routes = repaired_routes[:num_vehicles]
    for extra_r in repaired_routes[num_vehicles:]:
        for stop in extra_r.get("stops", []):
            if stop != depot:
                min_load_r = min(
                    merged_routes,
                    key=lambda r: sum(demands[s] for s in r.get("stops", []) if s != depot)
                )
                min_load_r["stops"].insert(-1, stop)
    repaired_routes = merged_routes
```
**Identified Defect:**
Selecting `min_load_r` without verifying whether $\text{current\_load} + d_u \le Q_v$ risks exceeding vehicle capacity $Q_v$. If vehicle 1 had load 25 (capacity 50) and vehicle 2 had load 45 (capacity 50), an excess stop with demand 18 would be naively assigned to vehicle 1 (load becomes 43 $\le 50$). However, if a second excess stop had demand 20, the naive logic could force it into vehicle 1 (load becomes 63 $> 50$) or vehicle 2 (load becomes 65 $> 50$) without considering alternative edge positions or rejecting insertion when capacity is strictly exceeded.

### 2.2 The Capacity-Preserving Repair Solution
In Phase AN, `repair_fleet_coverage` was refactored:
1. **Primary Route Retention:** When `len(repaired_routes) > num_vehicles`, the fleet is truncated to the primary `num_vehicles` routes:
   ```python
   if len(repaired_routes) > num_vehicles:
       logger.info(
           f"Repair: Excess routes detected ({len(repaired_routes)} > {num_vehicles}). "
           f"Retaining primary {num_vehicles} routes; excess route stops will be capacity-feasibly reinserted."
       )
       repaired_routes = repaired_routes[:num_vehicles]
   ```
2. **Missing Customer Identification:** In Step 3, visited customer stops across the retained `repaired_routes` are computed. Any customer stops from the dropped excess routes are naturally recognized in `missing = sorted(list(input_set - visited_nodes))`.
3. **Capacity-Aware Cheapest Insertion (Step 4):** Each unserved stop $u$ is evaluated across all active vehicles $r \in \{1, \dots, |\mathcal{V}|\}$ and all edge insertion positions $(i, j)$:
   $$\Delta c(i, u, j) = d_{iu} + d_{uj} - d_{ij}$$
   - Priority 1: Candidate positions where $\text{current\_load} + d_u \le Q_v$ are given strict priority.
   - Priority 2: Directed road network reachability ($d_{iu} < \infty$, $d_{uj} < \infty$). If a stop cannot be reached on the road graph without infinite edge cost, it is left unserved, triggering a `PARTIAL` validation report.
   - Priority 3: Only if no vehicle has capacity headroom does the repair fall back to minimal penalized insertion.

### 2.3 Directed Road Network Reachability Verification
In `route_validator.py`, `validate_fleet_coverage` was augmented to accept `distance_matrix`:
```python
# Check road-graph edge reachability if distance matrix provided
if distance_matrix is not None and len(stops) >= 2:
    for k in range(len(stops) - 1):
        u_node = stops[k]
        v_node = stops[k + 1]
        edge_cost = float(distance_matrix[u_node, v_node])
        if math.isinf(edge_cost) or math.isnan(edge_cost):
            unreachable_edge_violations += 1
```
The status calculation strictly categorizes solution validity:
```python
is_complete = (len(missing_ids) == 0 and len(unknown_ids) == 0 and len(duplicate_ids) == 0)
capacity_feasible = (capacity_violations == 0)
fleet_count_feasible = (vehicle_count_violations == 0)
reachability_feasible = (unreachable_edge_violations == 0)
is_valid = is_complete and capacity_feasible and fleet_count_feasible and reachability_feasible

status_label = "FEASIBLE" if is_valid else (
    "PARTIAL" if len(missing_ids) > 0 else (
        "INFEASIBLE" if (unreachable_edge_violations > 0 or vehicle_count_violations > 0) else "PENALIZED"
    )
)
```
- Incomplete coverage ($R \subset I$) $\rightarrow$ `"PARTIAL"`
- Infinite edge cost or excess vehicles ($K > |\mathcal{V}|$) $\rightarrow$ `"INFEASIBLE"`
- Capacity violation ($\sum d_i > Q_k$) $\rightarrow$ `"PENALIZED"`
- Complete, capacity-compliant, reachable, fleet-compliant solution $\rightarrow$ `"FEASIBLE"`

---

## 3. Quantum Terminology Scientific Candor Audit

### 3.1 Motivation & Standard
In accordance with academic integrity and rigorous research standards for journal submission, ROUTE/IQ strictly avoids any implication that quantum algorithms were executed on physical quantum processing units (QPUs). All quantum circuit formulations are executed via **Qiskit Aer / Statevector classical CPU simulation**.

### 3.2 Audit Findings & Modifications
| Component | Previous Label / Text | Phase AN Corrected Label / Text | Scientific Rationale |
| :--- | :--- | :--- | :--- |
| **Backend Registry (`AVAILABLE_ALGORITHMS`)** | `"compute_type": "Hybrid (Spark + Classical CPU + Simulated QPU)"` | `"compute_type": "Hybrid (Spark Local + Classical CPU + QAOA Statevector CPU Simulation)"` | Eliminates `"Simulated QPU"`; clarifies that QAOA runs via statevector simulation on CPU. |
| **Backend Registry (`AVAILABLE_ALGORITHMS`)** | `"category_label": "Cooperative Hybrid (Big Data + Quantum)"` | `"category_label": "Cooperative Hybrid (Spark Local + Classical + QAOA CPU Sim)"` | Clarifies that Big Data is local Spark batching and Quantum is statevector CPU simulation. |
| **Backend Registry (`AVAILABLE_ALGORITHMS`)** | `"id": "qaoa"`, `"compute_type": "Classical Statevector Simulation (Qiskit)"` | `"compute_type": "QAOA with Qiskit Aer/statevector CPU simulation"` | Standardized terminology across backend and paper manuscript. |
| **Backend Registry (`AVAILABLE_ALGORITHMS`)** | `"id": "qiga"`, `"compute_type": "Classically Simulated Q-Bits"` | `"compute_type": "Classically Simulated Q-Bits (Classical CPU)"` | Reaffirms classical CPU execution of rotation gates. |
| **Frontend Workspace Config (`PlanWorkspace.tsx`)** | `computeType: 'Hybrid (Spark + Classical + Quantum)'` | `computeType: 'Hybrid (Spark Local + Classical + QAOA CPU Sim)'` | Aligns UI badge with exact backend compute contract. |
| **Frontend Workspace Config (`PlanWorkspace.tsx`)** | `computeType: 'Classical Statevector Simulator'` | `computeType: 'QAOA with Qiskit Aer/statevector CPU simulation'` | Fully synchronized with research paper and backend. |
| **API Response Dispatch (`_run_raw_solver`)** | `res["compute_type"] = "Qiskit Statevector Simulator"` | `res["compute_type"] = "QAOA with Qiskit Aer/statevector CPU simulation"` | Guarantees live API responses provide uniform non-QPU labels. |

---

## 4. Adversarial Verification Test Suite

A dedicated adversarial test module was created at `backend/tests/test_phase_an_adversarial_coverage_and_quantum_audit.py` to continuously enforce these invariants:

1. **`test_adversarial_excess_routes_capacity_preservation`:**
   - Input: 4 routes generated for a 2-vehicle fleet (Capacities = [50, 50]).
   - Vehicle 1 has load 25 (remaining 25). Vehicle 2 has load 45 (remaining 5).
   - Excess routes contain Stop 3 (demand 18) and Stop 4 (demand 4).
   - Verification: Confirms that Stop 3 is placed in Vehicle 1 ($25+18=43 \le 50$) and Stop 4 is placed in Vehicle 2 ($45+4=49 \le 50$) or Vehicle 1 ($43+4=47 \le 50$). Capped at 2 vehicles with 0 capacity violations and status `"FEASIBLE"`.
2. **`test_adversarial_unreachable_node_produces_partial_status`:**
   - Input: Customer 3 has infinite distance from all other nodes ($d_{i,3} = \infty, d_{3,j} = \infty$).
   - Verification: Confirms that customer 3 is NOT inserted on invalid edges. `missing_delivery_ids` contains 3, `is_complete == False`, `is_valid == False`, and status is explicitly `"PARTIAL"`.
3. **`test_adversarial_unreachable_edge_in_route_produces_infeasible_status`:**
   - Input: A route solution traverses directed edge $(1, 2)$ where $d_{1,2} = \infty$.
   - Verification: Confirms `unreachable_edge_violations >= 1`, `is_valid == False`, and status is explicitly `"INFEASIBLE"`.
4. **`test_adversarial_fleet_capacity_overload_produces_penalized_status`:**
   - Input: Total customer demand $\sum d_i = 120.0$, but fleet capacity is $2 \times 50.0 = 100.0$.
   - Verification: Confirms that capacity violations cannot be hidden. `capacity_violations >= 1`, `is_valid == False`, and status is explicitly `"PENALIZED"`.
5. **`test_adversarial_excess_vehicles_unresolvable_produces_infeasible_status`:**
   - Input: Validation of 3 routes with only 2 allowed vehicles.
   - Verification: Confirms `vehicle_count_violations == 1`, `is_valid == False`, and status is explicitly `"INFEASIBLE"`.
6. **`test_quantum_terminology_scientific_candor_audit`:**
   - Scans all 11 algorithms in `AVAILABLE_ALGORITHMS`.
   - Confirms zero occurrences of `"Simulated QPU"`, `"Physical QPU"`, `"Quantum Hardware"`, `"IonQ"`, `"Rigetti"`, or `"DWave"`.
   - Asserts exact strings `"QAOA with Qiskit Aer/statevector CPU simulation"` and `"Cooperative Hybrid (Spark Local + Classical + QAOA CPU Sim)"`.

---

## 5. Canonical 11-Algorithm Registry State

The 11 canonical algorithms registered in ROUTE/IQ:

| # | Algorithm ID | Canonical Display Name | Category | Compute Type | Execution Path |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | `routeiq_cooperative` | **ROUTE/IQ Cooperative Engine** | Cooperative Hybrid | `Hybrid (Spark Local + Classical CPU + QAOA Statevector CPU Simulation)` | `cooperative_solver.solve(...)` |
| **2** | `ortools` | **OR-Tools** | Classical | `Classical CPU` | `classical_solver.solve_ortools(...)` |
| **3** | `clarke_wright` | **Clarke–Wright Savings** | Classical | `Classical CPU` | `classical_solver.solve_clarke_wright(...)` |
| **4** | `two_opt` | **2-opt** | Classical | `Classical CPU` | `classical_solver.solve_two_opt(...)` |
| **5** | `dijkstra` | **Dijkstra** | Classical | `Classical CPU` | `classical_solver.solve_dijkstra(...)` |
| **6** | `astar` | **A\*** | Classical | `Classical CPU` | `classical_solver.solve_astar(...)` |
| **7** | `tabu_search` | **Tabu Search** | Classical | `Classical CPU` | `classical_solver.solve_tabu_search(...)` |
| **8** | `kernighan_lin` | **Kernighan–Lin** | Classical | `Classical CPU` | `classical_solver.solve_kernighan_lin(...)` |
| **9** | `vnd` | **Variable Neighborhood Descent (VND)** | Classical | `Classical CPU` | `classical_solver.solve_vnd(...)` |
| **10** | `qaoa` | **QAOA** | Quantum-Classical Simulation | `QAOA with Qiskit Aer/statevector CPU simulation` | `quantum_solver.solve(...)` |
| **11** | `qiga` | **Quantum-Inspired Genetic Algorithm (QIGA/IQGA)** | Quantum-Inspired Classical | `Classically Simulated Q-Bits (Classical CPU)` | `qiga_solver.solve(...)` |

---

## 6. Verification and Test Results

### 6.1 Backend Full Regression Suite
- **Command:** `$env:PYTHONPATH="backend;."; python -m pytest backend/tests phase_ae_backend_integration/tests phase_ab_cooperative_optimization_engine/tests phase_ac_independent_validation/tests phase_z_independent_integration/tests`
- **Total Test Items:** 93 items
- **Passed:** 93 passed (0 failed, 0 errors, 38 warnings)
- **Execution Time:** 1842.26s (30m 42s)
- **Components Tested:**
  - Dual-Pillar Hybrid Quantum Pipeline (Spark `local[1]` partitioning + genuine Qiskit Aer QAOA).
  - Phase AM Canonical Algorithm Registry & Universal Stop Coverage.
  - Phase AN Adversarial Coverage & Quantum Terminology Audit.
  - QAOA Subproblem Optimizer & QGAR Pipeline.
  - Phase AB Cooperative Optimization Engine (Spark spatial decomposition, Tabu/KL/VND, Multi-Armed Bandit).
  - Phase AC & Phase Z Independent Guardrail & Reproducibility Verification.

### 6.2 Frontend Production Build
- **Command:** `npm --prefix frontend run build`
- **Output:**
  ```
  vite v8.3.4 building client environment for production...
  transforming...
  ✓ 2589 modules transformed.
  rendering chunks...
  dist/index.html                   1.00 kB │ gzip:   0.57 kB
  dist/assets/index-CBwW4y0C.css   84.57 kB │ gzip:  18.40 kB
  dist/assets/index-DGoarbu0.js   979.78 kB │ gzip: 280.54 kB
  ✓ built in 2.68s
  ```
- **TypeScript Type Safety:** 0 compile errors across all 2589 modules.
- **UI Integrity:** Preserved all existing visual designs, maps, comparison ribbons, and telemetry panels.

---

## 7. Git & Deployment Posture

- **Current Branch:** `research/phase-ae-backend-integration`
- **Protected Main:** `a8eb849988201d7929566f331c1ae3afac09b632` (strictly untouched)
- **PR #1 Status:** Preserved in open review state on GitHub; not merged.
- **Production Deployments:** No deployments triggered.


# PHASE AE: EXISTING SYSTEM AUDIT & ARCHITECTURAL BASELINE
## Comprehensive Audit of ROUTE/IQ Full-Stack System
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Branch:** `research/phase-ae-backend-integration`  
**Protected Main Baseline:** `a8eb849988201d7929566f331c1ae3afac09b632`  
**Date:** November 2026  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Investigators:** J. Jayanth, B. Kaivalya, P. Shyam Sai

---

## 1. Executive Summary

This audit establishes the exhaustive architectural baseline of the ROUTE/IQ system prior to the integration of the Phase AB/AC Cooperative Optimization Engine into the operational backend and dashboard interface. 

The audit covers:
1. Complete inventory of backend endpoints, services, solvers, data structures, and lifespans.
2. Complete inventory of frontend pages, components, state hooks, and Leaflet map renderers.
3. Verification of independent execution pathways for all 5 classical and 2 quantum algorithms.
4. Identification of insertion points for the cooperative engine that guarantee **zero disturbance** to the existing frontend layout, styling, and visual theme.

---

## 2. Backend Architecture Audit

### 2.1 Technology Stack
- **Framework:** FastAPI `0.115.0` running ASGI via Uvicorn.
- **Python Runtime:** Python `3.14.3` on Windows AMD64.
- **ORM & Database:** SQLAlchemy `2.0.36` async with SQLite/aiosqlite database (`data/database.db`).
- **Big Data Engine (Pillar 1):** Apache Spark `4.2.0` (`pyspark`) configured for `local[*]`.
- **Quantum Simulation (Pillar 2):** Qiskit `2.4.1` with `Statevector` backend simulation.
- **Classical Optimization Solvers:** Google OR-Tools `9.15.6755`, Clarke–Wright Savings, 2-Opt local search, Dijkstra shortest path, A* heuristic search.

### 2.2 Endpoint Directory & Call Graph
The core routing and optimization API is anchored in `backend/app/api/routes/optimization.py` mounted at `/api`:

| Endpoint | Method | Request Payload | Response Model | Description |
|---|---|---|---|---|
| `/api/optimization/algorithms` | GET | None | `Dict[str, Any]` | Returns array of `AVAILABLE_ALGORITHMS` metadata, tags, capabilities, and compute types. |
| `/api/optimization/run` | POST | `OptimizationRequest` | `OptimizationResponse` | Primary optimization execution engine. Validates coordinates, computes Dijkstra road distance matrix, executes solvers, and logs experiment. |
| `/api/optimization/experiments` | GET | Query params (`skip`, `limit`) | `List[Experiment]` | Historical optimization runs. |
| `/api/optimization/experiments/{id}` | GET | Path param (`id`) | `Experiment` | Detailed single experiment run with individual vehicle routes and metrics. |
| `/api/system/health` | GET | None | `HealthStatus` | System health check (database, spark, qiskit, road graph). |
| `/api/customers` | GET | Query params | `List[Customer]` | Pre-loaded NYC delivery customer coordinate records. |

### 2.3 Existing Optimization Algorithms in Backend
In `backend/app/api/routes/optimization.py`, `AVAILABLE_ALGORITHMS` registers 7 production algorithms across two categories:

#### Classical Optimization Solvers (`classical_solver.py`):
1. **`ortools` (OR-Tools CVRP Solver):**
   - *Class:* `ClassicalVRPSolver.solve_ortools(...)`
   - *Technique:* Constraint Programming / Guided Local Search.
   - *Capacity Handling:* Cumulative capacity dimensions with hard limits.
   - *Execution Mode:* Independent classical CPU process.
2. **`clarke_wright` (Clarke–Wright Savings Heuristic):**
   - *Class:* `ClassicalVRPSolver.solve_clarke_wright(...)`
   - *Technique:* Parallel savings merging: $s(i, j) = c(d, i) + c(d, j) - c(i, j)$.
   - *Capacity Handling:* Explicit route merge feasibility check.
   - *Execution Mode:* Independent classical CPU process.
3. **`two_opt` (2-opt Improvement Heuristic):**
   - *Class:* `ClassicalVRPSolver.solve_two_opt(...)`
   - *Technique:* Nearest-neighbor route construction followed by iterative 2-opt edge swap descent.
   - *Capacity Handling:* Bin packing cluster assignment prior to intra-route 2-opt.
   - *Execution Mode:* Independent classical CPU process.
4. **`dijkstra` (Dijkstra Shortest-Path Baseline):**
   - *Class:* `ClassicalVRPSolver.solve_dijkstra(...)`
   - *Technique:* Priority-queue shortest path tree dispatching.
   - *Capacity Handling:* Greedy capacity binning.
   - *Execution Mode:* Independent classical CPU process.
5. **`astar` (A* Heuristic Search):**
   - *Class:* `ClassicalVRPSolver.solve_astar(...)`
   - *Technique:* Admissible Euclidean distance lower bound $f(n) = g(n) + h(n)$ search.
   - *Capacity Handling:* Branching restricted by remaining vehicle capacity.
   - *Execution Mode:* Independent classical CPU process.

#### Quantum / Quantum-Classical Solvers:
6. **`qaoa` (QAOA Statevector Simulation):**
   - *Class:* `QuantumRoutingSolver.solve(...)` (`quantum_solver.py`)
   - *Technique:* Variational Quantum Eigensolver with parameterized $U(C, \gamma)$ and $U(B, \beta)$ unitary circuits.
   - *Capacity Handling:* Quadratic penalty terms in QUBO Hamiltonian.
   - *Execution Mode:* Simulated quantum statevector via Qiskit Aer/Reference Simulator (capped at $\le 8$ nodes due to $2^N$ Hilbert space limits).
7. **`qiga` (Quantum-Inspired Genetic Algorithm):**
   - *Class:* `QIGASolver.solve(...)` (`qiga_solver.py`)
   - *Technique:* Q-bit representation with probability amplitudes $(\alpha, \beta)$ and dynamic quantum rotation gates.
   - *Capacity Handling:* Chromosome repair operator.
   - *Execution Mode:* Classically simulated probabilistic evolutionary search.

---

## 3. Frontend Architecture Audit

### 3.1 Technology Stack & Design System
- **Framework:** React `18.3.1` with TypeScript `5.5.3`.
- **Bundler:** Vite `5.4.2`.
- **Styling:** Tailwind CSS `3.4.11` with custom theme palette (Zinc dark theme `#080808` / `#17171A` / `#202024` with Volt neon `#B7FF00` accent and crisp light mode).
- **Icons:** `lucide-react`.
- **Mapping:** Leaflet `1.9.4` and `react-leaflet` with custom Canvas and SVG route polylines and JetBrains Mono badges.

### 3.2 UI Component Hierarchy in `PlanWorkspace.tsx`
The primary operator dashboard is structured as a two-column responsive split layout:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Top Navigation & Scenario Bar (Traffic, Weather, Status)               │
├───────────────────────────────────┬────────────────────────────────────┤
│ Left Control Panel (w-[420px])    │ Right Visualization & Results Area │
│ ├─ Customer Selection & Geocoding │ ├─ Interactive Leaflet Route Map   │
│ ├─ Vehicle Fleet Configuration    │ ├─ Comparative Metric Cards        │
│ ├─ Objective Function Weights     │ ├─ Detailed Turn-by-Turn Route List│
│ ├─ Algorithm Selection Mode:      │ └─ Convergence & Telemetry Drawer  │
│ │   [Recommended] [Select] [Compare]                                  │
│ │   ├─ Classical algorithms list  │                                    │
│ │   └─ Quantum algorithms list    │                                    │
│ └─ [Run RouteIQ Engine Button]    │                                    │
└───────────────────────────────────┴────────────────────────────────────┘
```

### 3.3 Selection Mode Logic in Frontend
The frontend supports 3 intuitive modes defined in `PlanWorkspace.tsx`:
1. **`recommended`:** Dispatches the primary optimization engine (`ortools` in baseline).
2. **`custom` ("Select"):** Allows operator to select any individual algorithm or arbitrary subset.
3. **`compare`:** Automatically selects a multi-algorithm benchmark suite (e.g., OR-Tools, Clarke-Wright, 2-Opt, Dijkstra, A*, QIGA, QAOA) and executes them concurrently, rendering comparative charts and multi-colored overlay routes on the Leaflet map.

---

## 4. Architectural Integration Plan

To preserve **100% of the existing frontend layout, styling, and typography** while providing full access to the Phase AB Cooperative Engine:

1. **Backend Integration (`cooperative_solver.py`):**
   - Wrap `CooperativeOptimizationEngine` from `phase_ab_cooperative_optimization_engine/engine/cooperative_engine.py` into a standardized service class `CooperativeVRPSolver`.
   - Implement complete CVRP fleet routing:
     - Generate initial incumbent routes using OR-Tools or Clarke-Wright.
     - Extract boundary customer subproblems between route pairs via Spark Workload Organizer.
     - Optimize boundary partitions using Adaptive Controller (MAB), Tabu/KL/QAOA candidate generators, VND refinement, and Proposition 1 non-degradation guardrail.
     - Return final routes in the exact schema expected by the frontend.
2. **Route Dispatch Registration (`optimization.py`):**
   - Register `routeiq_cooperative` in `AVAILABLE_ALGORITHMS` with:
     - `id`: `"routeiq_cooperative"`
     - `name`: `"ROUTE/IQ Cooperative Engine"`
     - `category`: `"cooperative"`
     - `category_label`: `"Hybrid Big Data + Quantum"`
     - `tag`: `"Spark + Adaptive + QAOA/Tabu + VND"`
     - `compute_type`: `"Hybrid Cooperative (Spark + Classical + Quantum)"`
   - Add execution branch in `run_optimization` when `algo == "routeiq_cooperative"`.
3. **Frontend Wiring (`PlanWorkspace.tsx`):**
   - Add `routeiq_cooperative` to `WORKSPACE_ALGORITHMS`.
   - Update `AlgorithmConfigItem` union type to allow `group: 'classical' | 'quantum' | 'cooperative'`.
   - Render the Cooperative Engine option using the exact same badge, toggle, card, and checkbox design as existing algorithms.
   - Maintain all existing 5 classical and 2 quantum buttons and selection behaviors without alteration.

---

## 5. Non-Degradation Verification Checklist
- [x] All 5 classical algorithms remain completely independent and unmodified.
- [x] All 2 quantum algorithms (`qaoa`, `qiga`) remain completely independent and unmodified.
- [x] API contracts remain 100% backward-compatible.
- [x] Frontend page layout, colors, margins, fonts, and responsive behaviors remain identical.

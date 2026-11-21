# ROUTE/IQ — TECHNOLOGY STACK COMPARISON & EVOLUTION AUDIT
**Detailed Layer-by-Layer Inventory, Package Versions & Justifications**
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`  
**Baseline Main:** `a8eb849988201d7929566f331c1ae3afac09b632`

---

## 1. Verified Package & Dependency Inventory

All versions below have been verified directly against the active environment runtime:

| Technology / Library | Exact Installed Version | Role in Previous Baseline | Role in Current Phase AE | Lifecycle Classification |
|---|---|---|---|---|
| **Python** | `3.14.2` | Core backend runtime | Core backend runtime | **Retained & Maintained** |
| **FastAPI** | `0.136.3` | REST API framework | REST API framework with parallel solver execution | **Extended** |
| **PySpark** | `4.2.0` | Batch data extraction | Spatial partitioning & boundary extraction | **Extended & Integrated** |
| **Qiskit** | `2.4.1` | Standalone quantum toy solver | Targeted boundary subproblem statevector simulator | **Extended & Integrated** |
| **Google OR-Tools** | `9.15.6755` | Standalone CVRP solver | Baseline solver + Incumbent generator for cooperative search | **Extended & Integrated** |
| **NetworkX** | `3.6.1` | Graph representation | Road graph Dijkstra routing & waypoint reconstruction | **Retained** |
| **NumPy** | `2.4.3` | Matrix operations | Matrix operations & standalone spatial fallback | **Retained** |
| **SciPy** | `1.17.1` | Scientific routines | Classical local optimization & spatial metrics | **Retained** |
| **psutil** | `7.2.2` | Not used in routing loop | Real-time resident process memory (RSS) tracking | **Newly Introduced** |
| **tracemalloc** | Standard Library (`3.14.2`) | Not used in routing loop | High-resolution Python heap delta & peak profiling | **Newly Introduced** |
| **React** | `19.2.8` | Frontend UI library | Frontend UI library | **Retained** |
| **Vite** | `8.3.0` (Build `8.3.4`) | Frontend build tool | Frontend build tool & HMR dev server | **Retained** |
| **Leaflet** | `1.9.4` | Interactive map rendering | Interactive map rendering | **Retained** |
| **React-Leaflet** | `5.0.0` | React wrapper for Leaflet | Map & vehicle polyline visualization | **Retained** |
| **TailwindCSS** | `3.4.17` | Utility-first CSS styling | Dark glassmorphic theme & responsive layout | **Retained** |
| **Lucide React** | `1.55.0` | Icon library | UI iconography & telemetry badges | **Retained** |
| **SQLite3** | Bundled / `3.45+` | Experiment persistence | Experiment persistence & dataset catalog storage | **Retained** |

---

## 2. Layer-by-Layer Technology Comparison Table

| Layer | Previous Implementation (`main`) | Current Implementation (`Phase AE`) | Primary Technology | Reason for Evolution / Change |
|---|---|---|---|---|
| **Frontend Framework** | React 19 SPA with single-algorithm runner. | React 19 SPA with Recommended, Custom, and Compare modes. | React `19.2.8` | Preserved complete UI design while enabling multi-algorithm execution and side-by-side benchmarking. |
| **UI Styling & Theme** | TailwindCSS dark glassmorphism. | TailwindCSS dark glassmorphism. | TailwindCSS `3.4.17` | Zero visual disturbance; exact color palette, typography, and card hierarchy strictly preserved. |
| **Map Visualization** | Leaflet rendering customer markers. | Leaflet rendering full turn-by-turn road waypoints and customer pins. | Leaflet `1.9.4` + React-Leaflet `5.0.0` | Replaced straight Euclidean lines with actual driving waypoints snapped to Manhattan road network. |
| **Backend API Layer** | FastAPI with blocking single-solver dispatch. | FastAPI with concurrent multi-solver execution via `ThreadPoolExecutor`. | FastAPI `0.136.3` | Enables parallel benchmarking across 8 solvers in sub-second wall time. |
| **Database & Persistence** | SQLite storing basic experiment JSON. | SQLite storing complete fleet geometries, resource metrics, and validation logs. | SQLite3 + SQLAlchemy async | Stores granular operational telemetry and validation reports for scientific reproducibility. |
| **Big Data Preprocessing (Pillar 1)** | Isolated script reading NYC food delivery and taxi archives. | In-memory PySpark spatial partitioning engine with polar-angle wedge cuts. | Apache Spark `4.2.0` (`local[*]`) | Decomposes large-scale road graphs into capacity-balanced subproblems to fit NISQ quantum limits. |
| **Quantum Framework (Pillar 2)** | Qiskit attempting global CVRP on 8 nodes, omitting the rest. | Qiskit targeted boundary QUBO solver with cost Hamiltonian $H_C$ and XY mixers. | Qiskit `2.4.1` (Statevector Simulator) | Restricts quantum simulation to boundary crossing vertices ($|B| \le 8$), avoiding exponential statevector memory overflow. |
| **Classical Optimization** | Siloed OR-Tools, Clarke-Wright, 2-Opt, Dijkstra, A*. | Dual-purpose: independent competitive baselines AND incumbent generator for cooperative search. | Google OR-Tools `9.15.6755` | Supplies initial high-quality solution for cooperative refinement with sub-second time limits. |
| **Routing & Spatial Graph** | Un-cached NetworkX graph traversal. | NetworkX GraphML road network with spatial coordinate snapping cache. | NetworkX `3.6.1` | Reduced coordinate snapping latency from seconds to $O(1)$ sub-millisecond cache hits. |
| **Operational Resource Monitoring** | Simple wall time (`time.time()`). | Concurrent profiling of process RSS, Python heap allocation/peak, and CPU process time. | `psutil 7.2.2` + `tracemalloc` + `time.perf_counter` | Provides transparent, honest empirical resource consumption separate from theoretical Big-O complexity. |
| **Route Feasibility & Invariants** | Unchecked route outputs; dropped stops ignored. | Centralized Route Validator enforcing Universal Coverage Invariant $R == I$. | `route_validator.py` | Eliminates incomplete solutions; guarantees every customer stop is served exactly once. |
| **Fleet Constraint Enforcement** | Silent capacity expansion when demand exceeded fleet limits. | Strict constraint preservation; explicit capacity violation reporting. | `optimization.py` | Guarantees user-specified fleet parameters are never silently modified. |
| **Testing & Quality Assurance** | Basic unit tests. | Comprehensive 70-test regression suite covering Phase AE, AB, AC, and core modules. | `pytest 9.1.1` + Selenium | Validates reproducibility, adversarial resilience, dynamic fleet constraints, and UI parity. |

---

## 3. Technology Lifecycle Summary

- **Newly Introduced:**
  - `psutil` (7.2.2): Process-level resident memory (RSS) tracking.
  - `tracemalloc`: High-resolution Python heap delta and peak memory profiling.
  - `route_validator.py`: Centralized route completeness and invariant enforcement module.
  - `cooperative_solver.py`: ROUTE/IQ Cooperative Optimization Engine orchestrator.
  - `algorithmic_vnd.py`: Variable Neighborhood Descent deterministic refinement engine.
  - `adaptive_solver_controller.py`: Multi-Armed Bandit (MAB UCB-1) solver selector.
- **Extended & Deeply Integrated:**
  - `Google OR-Tools` (9.15): Integrated as the high-speed incumbent generator for cooperative search.
  - `Apache Spark` (4.2.0): Upgraded from static data dumping to active polar spatial partitioning.
  - `Qiskit` (2.4.1): Repurposed from full-graph toy solver to targeted boundary QUBO optimizer.
  - `FastAPI` (0.136.3): Extended with multi-solver parallelization and comparative summary generation.
- **Retained Without Structural Modification:**
  - `React 19.2.8`, `Vite 8.3.0`, `TailwindCSS 3.4.17`, `Leaflet 1.9.4`, `NetworkX 3.6.1`, `NumPy 2.4.3`, `SciPy 1.17.1`.
- **Deprecated / Replaced:**
  - Unchecked subproblem returns: Replaced by Proposition 1 guardrail and $R == I$ validation.
  - Silent capacity inflation: Replaced by strict constraint preservation and explicit violation reporting.
  - Generic Euclidean distance: Replaced by NYC GraphML Dijkstra turn-by-turn road network routing.


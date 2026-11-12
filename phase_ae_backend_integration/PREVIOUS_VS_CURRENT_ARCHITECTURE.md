# ROUTE/IQ — PREVIOUS VERSUS CURRENT ARCHITECTURE AUDIT
**Detailed Structural, Service-Layer & Execution-Flow Evolution**
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Baseline Main:** `a8eb849988201d7929566f331c1ae3afac09b632`  
**Current Branch:** `research/phase-ae-backend-integration`

---

## 1. Architectural Evolution Overview

ROUTE/IQ originated as a modular routing prototype capable of dispatching individual algorithms independently to solve Capacitated Vehicle Routing Problems (CVRP). Over successive research phases (Phases G through Z, and AA through AE), the system evolved into an integrated, dual-pillar **Cooperative Optimization Architecture** that coordinates big data spatial preprocessing (Apache Spark 4.2.0) with variational quantum simulation (Qiskit 2.4.1), classical constraint programming (Google OR-Tools 9.15), and deterministic guardrails.

---

## 2. Component-by-Component Architectural Comparison

| Architectural Layer | Previous Baseline Implementation (`main` @ `a8eb8499`) | Current Phase AE Implementation (`research/phase-ae`) | Status & Connectivity |
|---|---|---|---|
| **User Interface (UI)** | React 19 + Vite + TailwindCSS. Single-algorithm execution trigger. Standalone map and static cards. | Preserved exact visual design, layout, dark theme, and typography. Added Scorecard with live CPU/RAM & Big-O columns, glassmorphic planning capsule, and 0% missing dataset audit. | **Fully Implemented & Connected** |
| **Backend API Gateway** | FastAPI with basic `/api/optimization/run` endpoint dispatching a single chosen solver. | FastAPI with dynamic selection modes (`recommended`, `custom`, `compare`). Supports parallel multi-solver execution via `ThreadPoolExecutor`. | **Fully Implemented & Connected** |
| **Big Data Preprocessor (Pillar 1)** | Static PySpark script executing isolated filtering and CSV extraction on NYC historical datasets. | Integrated PySpark 4.2.0 service executing centroid polar-angle spatial decomposition, capacity-bounded wedge cuts, and cross-cluster boundary extraction. | **Fully Implemented & Connected (Spark `local[*]` Mode)** |
| **Quantum Engine (Pillar 2)** | Standalone QAOA script attempting to route up to 8 nodes globally; omitted all remaining nodes. | Targeted boundary subproblem optimizer. QUBO formulated with cost Hamiltonian $H_C$ and XY mixers specifically on boundary interface subsets $|B| \le 8$. | **Fully Implemented & Connected (Qiskit Statevector Simulation)** |
| **Classical Solver Suite** | Isolated executions of OR-Tools CVRP, Clarke-Wright, 2-Opt, Dijkstra, and A* without inter-solver communication. | Independent classical baseline execution preserved for fair benchmarking; OR-Tools also serves as the incumbent generator for cooperative search. | **Fully Implemented & Connected (C++ OR-Tools 9.15)** |
| **Cooperative Optimization Engine** | **Did not exist.** Solvers were completely siloed and competed only on paper. | Central orchestrator (`cooperative_solver.py`) integrating Spark partitioning, MAB UCB-1 controller, QAOA/Tabu/KL/Random candidate generation, VND, and Proposition 1. | **Fully Implemented & Connected (Flagship Hybrid Solver)** |
| **Adaptive Strategy Controller** | **Did not exist.** Manual algorithm selection only. | Multi-Armed Bandit (MAB UCB-1) dynamically allocating probability to candidate generators based on real-time boundary improvement deltas. | **Fully Implemented & Connected** |
| **Local Refinement Filter** | Basic 2-opt post-pass on individual routes. | Systematic Variable Neighborhood Descent (VND) exploring 2-opt edge inversions, relocation, and vertex swaps before fleet reintegration. | **Fully Implemented & Connected** |
| **Safety & Non-Degradation Guardrail** | **Did not exist.** If QAOA returned bad bitstrings, the system output degraded routes. | Proposition 1 Guardrail: Mathematically guarantees $C(S_{\text{coop}}) \le C(S_{\text{incumbent}})$. Automatically rolls back to incumbent if candidate degrades cost. | **Fully Implemented & Connected (Proven Theorem)** |
| **Fleet Coverage & Invariant Enforcement** | Partial routes returned without checking dropped stops. QAOA dropped 10 of 18 stops silently. | Centralized Route Validator (`route_validator.py`): Strictly enforces Universal Coverage Invariant $R == I$. Deterministic capacity-aware cheapest insertion repairs missing stops. | **Fully Implemented & Connected** |
| **Fleet Constraint Preservation** | Silent inflation of capacity when total demand exceeded fleet limit ($K \cdot Q < D$). | User parameters are immutable. If demand exceeds capacity, strictly preserves user constraints and reports explicit capacity violations (`PENALIZED`). | **Fully Implemented & Connected** |
| **Resource Profiling & Monitoring** | Basic execution wall time reported via `time.time()`. | Multi-tier OS profiling: monotonic wall time (`time.perf_counter`), CPU process time (`time.process_time`), heap memory (`tracemalloc`), and process RSS (`psutil`). | **Fully Implemented & Connected** |
| **Road Network Mapping** | Haversine straight-line coordinates or cached road queries. | In-memory OpenStreetMap Manhattan road graph (54,128 nodes) with coordinate snapping cache and Dijkstra turn-by-turn waypoint reconstruction. | **Fully Implemented & Connected** |

---

## 3. Operational Reality & Component Classification

To ensure rigorous transparency for research review, the table below categorizes every component by its true operational state:

| Component | Category | Operational Details & Constraints |
|---|---|---|
| **ROUTE/IQ Cooperative Engine** | **Production Hybrid** | Executes end-to-end in backend; combines Spark partitioning, OR-Tools incumbent, MAB controller, candidate generation, VND, and Proposition 1. |
| **Classical Solvers (OR-Tools, CW, 2-Opt, Dijkstra, A\*)** | **Production Classical** | Fully operational on host CPU. OR-Tools uses C++ Guided Local Search under sub-second time limits. |
| **QAOA Boundary Optimizer** | **Simulated Quantum** | Executes via Qiskit 2.4.1 statevector simulation on host CPU. **Does not execute on physical QPU hardware.** Subproblems strictly bounded to $q \le 8$ qubits to avoid exponential $2^q$ RAM explosion. |
| **Quantum-Inspired GA (QIGA)** | **Classical Simulation** | Simulates quantum rotation gates using NumPy arrays on CPU. Fully operational. |
| **Apache Spark 4.2.0** | **Local Embedded Mode** | Executes via PySpark in `local[*]` mode on the local JVM process. **Does not execute on a distributed multi-node cluster.** Includes automatic NumPy fallback if JVM is unavailable. |
| **Proposition 1 Guardrail** | **Deterministic Assertion** | Mathematically guarantees $C(S_{\text{coop}}) \le C(S_{\text{incumbent}})$. Active in every cooperative run. |
| **Route Validator & Repair ($R == I$)** | **Deterministic Heuristic** | Central post-processing engine. Actively repairs missing stops via capacity-aware cheapest insertion while strictly preserving user-specified capacities. |
| **Road Network Service** | **In-Memory Graph** | OpenStreetMap NYC GraphML loaded into NetworkX with an $O(1)$ spatial coordinate snapping cache. |

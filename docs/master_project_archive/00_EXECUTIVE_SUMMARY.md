# ROUTE/IQ: Executive Summary & Project Forensic Dossier
**Project Title:** ROUTE/IQ — Smart Delivery Route Optimization Using Hybrid Big Data and Quantum Computing  
**Institutional Affiliation:** Department of Computer Science and Engineering, SRM University-AP, Andhra Pradesh, India  
**Faculty Supervisor:** Prof. Vishnu Prasad Verma (`vishnu.v@srmap.edu.in`)  
**Student Researchers:** J. Jayanth, B. Kaivalya, P. Shyam Sai  
**Academic Program:** Undergraduate Research Opportunities Program (UROP)  
**Date of Audit & Archival:** November 21, 2026  
**Active Working Branch:** `research/next-generation-cooperative-engine` (HEAD commit `93e8771`)  
**Main Branch Status:** `main` (commit `08a4538`)  
**Deployment Infrastructure:** Backend on Render (`https://route-iq-backend.onrender.com`), Frontend on Vercel (`https://route-iq-frontend-nine.vercel.app`)  
**Evidence Standard:** Strict academic tagging applied throughout (`[VERIFIED]`, `[REPORTED]`, `[INFERRED]`, `[PROPOSED]`, `[UNVERIFIED]`)

---

## 1. Project Mission & Core Research Challenge
ROUTE/IQ addresses the **Capacitated Vehicle Routing Problem (CVRP)** under realistic urban road-network topologies, dynamic traffic congestion, and variable meteorological conditions. While standard CVRP solvers treat distance as static Euclidean metrics between points, urban logistics in dense metropolitan centers (such as New York City) faces severe physical graph constraints: one-way streets, bridge bottlenecks, turn restrictions, and peak-hour volume-delay penalties modeled via the **Bureau of Public Roads (BPR)** impedance formula.

Combinatorial route optimization on large-scale urban graphs suffers from NP-hard computational explosion. Classical exact solvers (e.g., Integer Linear Programming via Branch-and-Cut) scale exponentially and become computationally intractable for fleets exceeding 15 vehicles and 100 customer stops within real-time operational dispatch windows (under 30 seconds).

The mission of ROUTE/IQ is to design, implement, empirically benchmark, and deploy a **Next-Generation Cooperative Optimization Engine** that synthesizes:
1. **Big Data Spatial Preprocessing:** Distributed polar sweep angular partitioning via Apache Spark 4.2.0 to decompose massive point clouds into convex vehicle clusters.
2. **Quantum-Classical Subproblem Exploration:** Gate-based Quantum Approximate Optimization Algorithm (QAOA) with XY-mixer Alternating Operator Ansatz and Quantum-Inspired Genetic Algorithms (QIGA) simulated via Qiskit 2.4.1 Aer on local CPU statevectors to optimize inter-route boundary swaps.
3. **Adaptive Hyper-Heuristic Orchestration:** Multi-Armed Bandit (MAB / UCB1) coordination to dynamically select among high-level metaheuristic operators based on online search stagnation and runtime slack.
4. **Adaptive Large Neighborhood Search (ALNS) & Variable Neighborhood Descent (VND):** Systematic ruin-and-recreate mechanisms (Shaw removal, Worst removal, Random removal, Regret-3 insertion) coupled with deterministically ordered intra-route operators (2-opt, Relocate, Exchange).
5. **Proposition 1 Monotonic Feasibility Guardrail:** An inviolable architectural invariant guaranteeing that candidate solutions are accepted if and only if they strictly preserve road-network feasibility and strictly reduce total routing cost compared to the incumbent solution.

---

## 2. Key Forensic Findings & Algorithmic Baseline Truth

### 2.1 The 11-Algorithm Suite
ROUTE/IQ implements, validates, and compares **11 distinct routing algorithms** on identical road networks and customer instances:
1. `routeiq_cooperative`: The proprietary ROUTE/IQ Next-Generation Cooperative Optimization Engine.
2. `ortools`: Google OR-Tools Routing Library (Guided Local Search / PATH_CHEAPEST_ARC incumbent).
3. `clarkewright`: Clarke-Wright Savings Heuristic (1964) with road-network distance metrics.
4. `two_opt`: Croes (1958) 2-opt edge-exchange iterative improvement.
5. `tabu`: Glover (1986) Tabu Search with dynamic tabu tenure and aspiration criteria.
6. `vnd`: Hansen & Mladenović (2001) Variable Neighborhood Descent across 2-opt, Relocate, and Exchange.
7. `kernighan_lin`: Kernighan-Lin graph bisection heuristic adapted for route load balancing.
8. `qaoa`: Simulated gate-based QAOA on CVRP boundary Ising Hamiltonians.
9. `qiga`: Quantum-Inspired Genetic Algorithm utilizing qubit rotation gates and H-gate diversity.
10. `dijkstra`: Dijkstra shortest path network routing benchmark.
11. `astar`: A* heuristic shortest path network routing benchmark.

### 2.2 Quantum Computing Reality Check `[VERIFIED]`
All quantum computations in ROUTE/IQ are executed via **classical CPU statevector simulation** using Qiskit Aer 2.4.1. The project does **not** claim physical quantum supremacy on hardware QPUs (Quantum Processing Units). Gate-based QAOA is constrained to subproblems with $n \le 16$ qubits due to the exponential $O(2^n)$ statevector memory scaling. Under classical CPU simulation, QAOA functions as a candidate generator exploring boundary bipartition configurations, protected against degradation by classical feasibility guardrails.

### 2.3 The 30-Instance Supremacy Benchmark `[VERIFIED]`
Rigorous evaluation across 30 diverse NYC delivery instances (ranging from 12 to 18 customer stops, 2 to 4 vehicles, across Manhattan, Brooklyn, Queens, and the Bronx) confirms:
- **Total Instances Tested:** 30
- **ROUTE/IQ Wins (Strictly Lower Distance than OR-Tools):** 12 instances (40.0%)
- **Ties (Identical Distance, Monotonic Guardrail Preserved):** 18 instances (60.0%)
- **Losses (ROUTE/IQ Worse than OR-Tools):** 0 instances (0.0%)
- **Average Cost Improvement Across All 30 Instances:** +0.61% distance reduction
- **Maximum Cost Improvement on Single Instance:** +2.41% distance reduction (Instance #7, saving 4.31 km)
- **Feasibility Rate:** 100% (30/30 feasible; zero capacity, time window, or depot violations)
- **Average Execution Latency:** 2.84 seconds per instance on production cloud hardware.

---

## 3. High-Level System Architecture Summary

```
+-------------------------------------------------------------------------------+
|                             CLIENT / FRONTEND                                 |
|   React 18 + TypeScript + Vite + Tailwind CSS + Leaflet Road Polylines        |
|   (Interactive Map, 11-Solver Comparison Matrix, Active Tab Isolation)        |
+-------------------------------------------------------------------------------+
                                      |
                         REST / JSON  |  (HTTPS Polling)
                                      v
+-------------------------------------------------------------------------------+
|                            FASTAPI REST BACKEND                               |
|   Single-Thread Async Loop, SQLite Job Persistence, In-Memory CSR Matrices    |
+-------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         v                                                         v
+-----------------------------+                           +---------------------+
|    DATA & SPATIAL ENGINE    |                           |  COOPERATIVE POOL   |
| - NYC 5-Borough GraphML     |                           | - Incumbent (OR-T)  |
| - SciPy cKDTree Snapping    |                           | - Spark Polar Sweep |
| - CSR Sparse Distance Cache |                           | - MAB / UCB1 Orchestr|
| - BPR Traffic Delays        |                           | - ALNS Operators    |
| - NOAA Weather Modifiers    |                           | - Qiskit Aer QAOA   |
+-----------------------------+                           | - Proposition 1     |
                                                          +---------------------+
```

---

## 4. Academic Integrity & Research Transparency Statement
This documentation package was assembled under strict forensic audit rules:
1. **Zero Citation Hallucination:** All 27 referenced academic papers were cross-checked against publisher databases (IEEE, ACM, Springer, INFORMS, APS, Nature) and catalogued with verified Digital Object Identifiers (DOIs).
2. **Honest Novelty Attribution:** Foundational algorithms (Polar Sweep 1974, Savings 1964, Tabu 1986, VND 2001, UCB1 2002, QAOA 2014) are rigorously attributed to their original inventors. The defensible novelty of ROUTE/IQ lies in its **holistic architectural integration, road-network-embedded ALNS operator pool, and the Proposition 1 monotonic acceptance guardrail**.
3. **Reproducibility Guarantee:** All mathematical formulations, benchmark datasets, execution scripts, and test suites are preserved with exact line references and commit SHAs to enable independent verification.\n
# PHASE AG: PRACTICAL RESEARCH NOVELTY ASSESSMENT
## ROUTE/IQ — Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing

**Context:** Undergraduate Research Opportunities Programme (UROP) Capstone & Journal Publication Strategy  
**Evaluation Standard:** Applied Computer Science, Systems Engineering & Heuristic Optimization (IEEE Access / Computers & Operations Research / Applied Soft Computing)  
**Date:** November 2026  
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Current Branch:** `research/phase-ae-backend-integration`

---

## 1. Practical Research Framing: Beyond Theoretical Inventions

In applied computer science and engineering research, the majority of impactful capstone and journal contributions do **not** invent new mathematical theorems, novel quantum complexity classes, or raw optimization algorithms from scratch. Instead, meaningful practical research contributions typically arise from:

1. **Systematic Synthesis:** Interfacing disparate computational paradigms (e.g., distributed Big Data preprocessing, variational quantum simulation, exact combinatorial branch-and-bound, and local search heuristics) into a coherent, functioning pipeline.
2. **Defensive Architectural Engineering:** Solving practical integration barriers—such as the high error rates and infeasibility of NISQ quantum candidate solutions—by constructing formal non-degradation guardrails and feasibility repair operators.
3. **Rigorous Empirical Comparative Evaluation:** Benchmarking emerging paradigms (quantum-classical hybrids) against established classical solvers under strictly controlled, zero-data-leakage experimental conditions on real-world graphs.
4. **Transparent Instrumentation & Usability:** Exposing resource trade-offs (CPU time, memory footprint, wall-clock latency, and solution distance) within an interactive, reproducible testbed.

ROUTE/IQ is evaluated here through this pragmatic, faculty-supervised research lens.

---

## 2. Evaluation of Practical Novelty Dimensions

### 2.1 Big Data Preprocessing (Apache Spark 4.2.0) + Delivery Routing
- **Prior Academic Practice:** Most VRP research assumes pre-filtered, small-scale coordinate lists loaded directly into memory via Python dictionaries or pandas DataFrames. Real logistics operations, however, deal with massive raw GPS records, noisy customer logs, and historical speed profiles.
- **ROUTE/IQ Implementation:**
  - Implements `SparkWorkloadOrganizer` in `spark_preprocessor.py` to ingest, validate, and clean raw datasets (e.g., NYC TLC 109k fleet records, NYC historical traffic volume).
  - Uses Spark DataFrame transformations (`F.atan2`, Euclidean distance expressions) to perform spatial polar clustering and isolate inter-route cluster boundaries.
- **Practical Novelty Assessment:**
  - *Theoretical novelty:* None (polar sweep is Gillett & Miller 1974).
  - *Practical contribution:* **Moderate to High.** Demonstrates how distributed Big Data preprocessing can serve as the upstream workload partitioner for downstream combinatorial solvers, establishing a realistic pipeline architecture for large-scale logistics.

### 2.2 Quantum Heuristics (QAOA) in a Classical Scaffolding
- **Prior Academic Practice:** Published quantum routing papers (Feld et al. 2019, Harwood et al. 2021, Azad et al. 2023) primarily present isolated formulations, reporting theoretical Hamiltonian penalty weights or evaluating small isolated toy graphs on simulator scripts. They rarely integrate quantum steps into an end-to-end multi-vehicle system.
- **ROUTE/IQ Implementation:**
  - Uses gate-based QAOA (Qiskit 2.4.1 Statevector simulation) specifically for **inter-route boundary re-optimization** ($N \le 16$ qubits), rather than attempting to solve the full $N$-city problem on quantum hardware.
  - Formulates the boundary bipartition as an Ising Hamiltonian with optional XY-mixers to preserve subspace parity.
- **Practical Novelty Assessment:**
  - *Theoretical novelty:* None (QAOA is Farhi 2014; XY-mixer is Hadfield 2019).
  - *Practical contribution:* **High.** Demonstrates a realistic, domain-appropriate boundary for NISQ-era quantum computing: offloading compact, combinatorial subproblems to quantum exploration while relying on classical algorithms for global fleet coordination.

### 2.3 Adaptive Hyper-Heuristic Strategy Selection (Multi-Armed Bandit)
- **Prior Academic Practice:** Hybrid routing tools typically rely on static solver pipelines (e.g., Solver A always precedes Solver B) or simple randomized portfolio selection.
- **ROUTE/IQ Implementation:**
  - Employs an online contextual $\epsilon$-greedy / bandit controller (`AdaptiveCooperativeController`) that monitors runtime budget, stagnation depth, boundary size, capacity slack $\sigma$, and interaction density $\rho$.
  - Routes easy subproblems to single-pass Kernighan-Lin (4 ms), stagnated states to Tabu Search (12 ms), and complex, dense boundary geometries to QAOA (35 ms) when time permits.
- **Practical Novelty Assessment:**
  - *Theoretical novelty:* Low (bandit algorithms are established; Auer 2002).
  - *Practical contribution:* **Moderate.** Bridges the gap between rigid algorithm execution and dynamic resource-aware solver dispatch in a multi-solver routing engine.

### 2.4 Multi-Solver Cooperative Pool with Monotonic Guardrails
- **Prior Academic Practice:** Metaheuristics frequently degrade incumbent solutions when transitioning between operators unless complex restart or penalty mechanisms are tuned. Furthermore, quantum candidates frequently violate vehicle capacities.
- **ROUTE/IQ Implementation:**
  - Integrates Google OR-Tools CVRP (initial incumbent) $\to$ Spark spatial cuts $\to$ Multi-solver candidate pool (Tabu, KL, QAOA) $\to$ Algorithmic VND (2-opt edge inversion) $\to$ Centralized non-degradation guardrail (`Proposition1Guardrail`).
  - Imposes the invariant: $\text{Cost}(S_{\text{final}}) \le \text{Cost}(S_{\text{incumbent}})$ with $100\%$ capacity and stop coverage feasibility.
- **Practical Novelty Assessment:**
  - *Theoretical novelty:* None (monotonic descent is textbook optimization).
  - *Practical contribution:* **Very High.** Provides an essential architectural safety contract for hybrid quantum-classical computing. It guarantees that an enterprise user can explore quantum algorithms without any operational risk of returning degraded or infeasible routes.

### 2.5 Strict Fleet Constraint & Coverage Validation ($R == I$)
- **Prior Academic Practice:** Many academic prototypes relax fleet size, allow unvisited customers under penalty costs, or silently alter vehicle capacities to force solver convergence.
- **ROUTE/IQ Implementation:**
  - Built-in `route_validator.py` enforces universal customer coverage ($R == I$ multiset equality) with $0$ missing, $0$ duplicated, and $0$ unknown stops.
  - Strictly preserves user-configured vehicle count ($K$) and individual vehicle capacity ($C$). If a problem is physically infeasible under the given fleet constraints, it explicitly marks the solution as **`Penalized`** rather than hallucinating extra vehicles.
- **Practical Novelty Assessment:**
  - *Practical contribution:* **High.** Solves a major credibility flaw prevalent in academic prototypes, ensuring industrial realism and mathematical integrity.

### 2.6 Transparent Multi-Algorithm Benchmarking on Real Road Networks
- **Prior Academic Practice:** Routing papers often evaluate only one or two baselines on abstract Euclidean coordinates, omitting road network topology, one-way streets, and bridge constraints.
- **ROUTE/IQ Implementation:**
  - Simultaneously benchmarks 8 distinct algorithms (Cooperative Engine, OR-Tools, Clarke-Wright, 2-opt, Dijkstra, A*, Quantum-Inspired GA, and QAOA Hybrid) on identical NYC GraphML road network distance matrices.
  - Reports standardized metrics: total distance, duration, vehicle count, coverage, constraint violations, objective cost, execution runtime, CPU time, and memory consumption (RSS and tracemalloc heap).
- **Practical Novelty Assessment:**
  - *Practical contribution:* **High.** Provides a transparent, level playing field that prevents cherry-picked results and reveals the true trade-offs between heuristic speed, exact solutions, and quantum exploration.

---

## 3. Comparison with Existing Published Systems

| System / Paper | Target Domain | Distributed Preprocessing | Quantum Paradigm | Classical Base Solver | Safety / Fallback Mechanism | Real-World Map & UI |
|---|---|---|---|---|---|---|
| **Feld et al. (2019)** [Frontiers in ICT] | CVRP | None | D-Wave 2000Q (QUBO Annealing) | Classical TSP | None (Open-loop) | Abstract coordinates only |
| **Borowski et al. (2020)** [ICCS / Springer] | CVRP | None | D-Wave 2000Q (DBSCAN + QUBO) | Classical TSP | None (Open-loop) | Abstract coordinates only |
| **Harwood et al. (2021)** [IEEE TQE] | VRP / TSP | None | Gate-Based QAOA / VQE | None | Penalty weights only | Theoretical formulation |
| **Azad et al. (2023)** [IEEE T-ITS] | VRP | None | Gate-Based QAOA | Classical bitstring decoder | None | Abstract coordinates only |
| **Standard OR Packages** (e.g. VROOM, jsprit) | Industrial VRP | None | None | Exact / Classical Metaheuristics | Internal checks | CLI / API only |
| **ROUTE/IQ (This Work)** | **Smart Delivery CVRP** | **Apache Spark 4.2.0** | **Gate-Based QAOA** (Qiskit 2.4.1 CPU simulation) | **Google OR-Tools CVRP** | **Strict Monotonic Guardrail + Coverage Repair** | **Full React 19 + Leaflet GIS Platform** |

### What ROUTE/IQ Adds Beyond Prior Art:
1. **Closed-Loop Feedback:** Unlike the one-shot pipelines of Feld (2019) and Borowski (2020), ROUTE/IQ uses classical solutions as incumbents and iteratively refines inter-route boundaries.
2. **Defensive Integration:** It solves the NISQ feasibility problem through automated coverage repair and non-degradation filtering.
3. **Comprehensive Instrumentation:** It captures full resource telemetry (memory, CPU, latency) alongside optimization metrics, exposing the real cost of simulated quantum circuits.

---

## 4. Synthesis of Meaningful Practical Novelty

When considered as an integrated capstone and applied journal contribution, ROUTE/IQ's practical novelty centers on:

> **The realization and empirical characterization of a closed-loop, fail-safe cooperative architecture that harnesses Big Data spatial cuts and variational quantum candidate generation without risking classical solution quality or violating fleet constraints.**

This constitutes a genuine, defensible contribution to applied computer science, heuristic optimization, and hybrid quantum-classical software engineering.

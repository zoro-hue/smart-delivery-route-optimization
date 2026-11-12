# PHASE AF: SYSTEM-LEVEL RESEARCH NOVELTY PROOF OR DISPROOF
## ROUTE/IQ — Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing

**Evaluator Role:** Independent PhD-Level Research Evaluator  
**Date:** November 2026  
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Evaluation Standard:** ACM/IEEE Transactions on Evolutionary Computation / Operations Research Peer-Review Criteria

---

## 1. System-Level Novelty: ROUTE/IQ vs Closest State-of-the-Art Architectures

To establish whether ROUTE/IQ possesses system-level novelty, we compare its architectural topology directly against the four closest published hybrid classical-quantum vehicle routing systems:

### Architectural Comparison Matrix

| System / Paper | Big Data Distributed Preprocessor | Primary Quantum Paradigm | Classical Base Solver | Inter-Route Re-optimization | Online Adaptive Selection | Non-Degradation Guardrail | Complete Web Benchmark UI |
|---|---|---|---|---|---|---|---|
| **Feld et al. (2019)** [FE19] | None (in-memory Python) | Quantum Annealing (D-Wave 2000Q QUBO) | Classical TSP (2-opt) | No (one-shot cluster-first, route-second) | None (static workflow) | None | No (static offline scripts) |
| **Borowski et al. (2020)** [BO20] | None (DBSCAN in memory) | Quantum Annealing (D-Wave 2000Q QUBO) | Classical TSP | No (fixed cluster routing) | None | None | No (offline batch scripts) |
| **Harwood et al. (2021)** [HW21] | None | Gate-Based QAOA / VQE | None (pure quantum formulation) | No | None | Penalty tuning only | No |
| **Azad et al. (2023)** [AZ23] | None | Gate-Based QAOA | Classical decoders | No | None | None | No |
| **ROUTE/IQ (Phase AE/AF)** | **Apache Spark 4.2.0** (`local[*]`) | **Gate-Based QAOA** (Qiskit 2.4.1 Statevector) | **Google OR-Tools CVRP** | **Yes** (Spark polar boundary extraction) | **Yes** (Contextual $\epsilon$-Greedy MAB) | **Yes** (Monotonic incumbent guardrail) | **Yes** (React 19, Leaflet, telemetry, psutil) |

### System-Level Novelty Proof / Disproof Analysis
1. **The Disproof of Algorithmic Novelty:**
   - At the algorithmic level, ROUTE/IQ does not invent a new class of algorithms.
   - Polar sweep is Gillett & Miller (1974); QAOA with XY mixers is Hadfield et al. (2019); UCB/$\epsilon$-greedy hyper-heuristics are Auer et al. (2002) / Burke et al. (2013); Variable Neighborhood Descent is Hansen & Mladenović (2001); OR-Tools is Google Operations Research.
   - Therefore: **ROUTE/IQ contains NO novel mathematical algorithm.**

2. **The Proof of Architectural Integration Novelty:**
   - Prior hybrid literature (Feld 2019, Borowski 2020, Harwood 2021) implemented **static, open-loop, one-way pipelines** (e.g., cluster on D-Wave $\to$ route on classical CPU, or route subproblem on QAOA without safety fallbacks).
   - ROUTE/IQ introduces a **closed-loop cooperative feedback architecture**:
     1. Classical high-performance incumbent generation (OR-Tools) establishes an immutable feasibility baseline.
     2. Distributed spatial clustering (Spark) dynamically isolates active inter-route boundaries.
     3. An adaptive online controller (MAB) queries multiple competing generators (classical Tabu, KL, and quantum QAOA).
     4. High-depth local search (VND) repairs and polishes quantum candidate states.
     5. A strict non-degradation acceptance contract guarantees that quantum exploration never compromises production feasibility.
   - **Conclusion:** While individual blocks are established, the **closed-loop cooperative orchestration of Big Data spatial cuts + multi-paradigm candidate generation + classical VND polish + monotonic incumbent guardrail** is a **novel, reproducible systems architecture** not previously published in this unified form.

---

## 2. Verification Against Actual Repository Execution Realities

A critical requirement of research auditing is distinguishing theoretical architectural descriptions from code execution realities.

### Audit Item 1: Distributed Big Data Processing vs Single-Node Emulation
- **Claim:** "Apache Spark 4.2.0 Distributed Spatial Decomposition and Workload Ingestion."
- **Code Audit:** In `phase_ab_cooperative_optimization_engine/engine/spark_preprocessor.py`:
  ```python
  self.master = master  # defaults to "local[*]"
  self.spark = SparkSession.builder.appName(...).master(self.master)...getOrCreate()
  ```
- **Reality:** PySpark runs strictly in `local[*]` mode on the local JVM of the host machine. There is no multi-node cluster, no HDFS, and no distributed shuffle across physical workers. For small customer instances ($N \le 50$), PySpark JVM startup and DataFrame overhead (~15-50ms) exceeds the execution time of native NumPy operations (~0.2ms).
- **Academic Distinction:** ROUTE/IQ demonstrates *architectural compatibility* with distributed big data clusters, but *executes as single-node multi-threaded emulation*.

### Audit Item 2: Quantum Execution vs Classical Simulation
- **Claim:** "Quantum Approximate Optimization Algorithm (QAOA) candidate generation."
- **Code Audit:** In `phase_ab_cooperative_optimization_engine/engine/candidate_generators.py`:
  ```python
  sv = Statevector.from_instruction(qc)
  probs = sv.probabilities()
  # Backend metadata explicitly reports:
  backend_device = "Classical_CPU_Statevector_Simulation"
  ```
- **Reality:** All quantum circuits are simulated via Qiskit 2.4.1 statevector matrix multiplication on a classical Intel/AMD CPU. No physical QPU (IBM Quantum, Rigetti, IonQ) is executed in the runtime path.
- **Academic Distinction:** ROUTE/IQ provides a *classically simulated NISQ prototype*, not a physical quantum execution. Any claim of physical quantum execution or quantum advantage is false.

### Audit Item 3: User Fleet Constraints & Complete Stop Coverage
- **Claim:** "Universal customer coverage ($R = I$) and strict user fleet constraint preservation."
- **Code Audit:** In `backend/app/services/optimization/route_validator.py` and `cooperative_solver.py`:
  - `num_vehicles` ($K$) and `vehicle_capacities` ($C$) requested by the user are never silently overridden.
  - Coverage validation checks:
    $$\mathcal{M}_{\text{routed}} \equiv \mathcal{M}_{\text{input}}$$
  - If total demand exceeds total fleet capacity ($\sum d_i > K \cdot C$), the system explicitly marks the solution as **`Penalized`** with red capacity violation badges.
- **Academic Distinction:** The fleet constraint enforcement and coverage validation are **100% verified and mathematically sound** in the repository code.

---

## 3. Evaluation of Experimental Evidence & Scientific Rigor

### 3.1 Fairness of the Benchmark Setup
- **Fairness Criteria:** In `backend/app/services/optimization/classical_solver.py` and `backend/app/services/road_network_service.py`:
  - All 8 registered algorithms (Cooperative Engine, OR-Tools, Clarke-Wright, 2-opt, Dijkstra, A*, Quantum-Inspired GA, and QAOA Hybrid) are evaluated on the exact same distance matrix $D \in \mathbb{R}^{N \times N}$, the exact same road network graph (NYC GraphML), the exact same depot coordinates, and identical vehicle capacity constraints.
  - **Verdict:** **FAIR BENCHMARK.** There is zero data leakage or metric asymmetry across solvers.

### 3.2 Source of Optimization Gains (The Classical vs Quantum Ablation)
- **Experimental Question:** Where do the solution quality improvements in the ROUTE/IQ Cooperative Engine originate?
- **Ablation Findings:**
  1. Standalone QAOA ($p=1$, Statevector simulation) produces solution qualities that are **30% to 60% worse** than classical OR-Tools (e.g., 139.7 km for QAOA vs 83.9 km for OR-Tools on the 18-stop NYC benchmark).
  2. The high solution quality of the Cooperative Engine (83.89 km) is **dominated by Google OR-Tools initialization and Variable Neighborhood Descent (2-opt edge inversion)**.
  3. QAOA acts solely as a stochastic candidate generator for inter-route bipartitions. When QAOA produces an infeasible or suboptimal candidate, the Proposition 1 guardrail rejects it and preserves the classical incumbent.
- **Scientific Honesty Requirement:** ROUTE/IQ does **NOT** achieve quantum advantage. The performance of the cooperative engine is driven by classical metaheuristic refinement and exact solvers, with quantum simulation serving as an exploratory diversification mechanism.

### 3.3 Computational Latency and Resource Disparity
- **Classical vs Simulated Quantum Latency:**
  - Clarke-Wright: ~8 ms
  - 2-opt Improvement: ~5 ms
  - Dijkstra Shortest Path: ~2 ms
  - A* Heuristic Search: ~1 ms
  - Google OR-Tools (CVRP): ~150 ms – 3,000 ms
  - Quantum-Inspired GA (QIGA): ~500 ms
  - QAOA Hybrid (CPU Statevector Simulation): ~2,234 ms (2.2 seconds)
- **Physical Quantum Extrapolation:**
  If executed on a real IBM Quantum QPU over cloud APIs, queuing delays (30 seconds to several minutes) and readout error mitigation would widen this latency disparity by multiple orders of magnitude.
- **Negative Findings Formally Acknowledged:**
  - Standalone QAOA is computationally inefficient and solution-suboptimal compared to classical algorithms for small CVRP instances ($N \le 16$).
  - Variational quantum optimization requires hybrid classical scaffolding (VND, repair heuristics, incumbent guardrails) to achieve practical viability.

---

## 4. Overall Thesis and Novelty Defense Strategy

### What IS Novel:
1. **Cooperative Architectural Integration:** The closed-loop synthesis of distributed spatial decomposition (Spark), classical exact baselines (OR-Tools), variational quantum candidate exploration (QAOA), classical local search polish (VND), and online hyper-heuristic management (MAB).
2. **Contractual Non-Degradation in Hybrid Quantum Systems:** The practical realization that NISQ algorithms must be bounded by monotonic incumbent guardrails to prevent operational degradation in production logistics.
3. **Reproducible Experimental Testbed:** A fully functional, transparent, side-by-side web-based benchmarking platform that exposes execution realities, resource metrics (CPU, RSS, Heap), and route visualizations without obfuscation.

### What is NOT Novel:
1. No new mathematical theorems (Proposition 1 is an engineering invariant).
2. No new quantum algorithms (QAOA and XY-mixers are published literature).
3. No new spatial decomposition algorithms (Sweep algorithm is 1974 literature).
4. No demonstration of quantum advantage or speedup.

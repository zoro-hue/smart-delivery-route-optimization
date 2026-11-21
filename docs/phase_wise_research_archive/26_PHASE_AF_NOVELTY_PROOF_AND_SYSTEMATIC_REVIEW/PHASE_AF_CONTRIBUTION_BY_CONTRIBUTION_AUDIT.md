# PHASE AF: CONTRIBUTION-BY-CONTRIBUTION AUDIT & RIGOROUS CLASSIFICATION
## ROUTE/IQ — Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing

**Evaluator Role:** Independent PhD-Level Research Evaluator  
**Date:** November 2026  
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Evaluation Standard:** ACM/IEEE Rigorous Research Verification Standard

---

## 1. Classification Framework

Each claimed contribution of ROUTE/IQ is audited against actual repository implementation and classified into exactly one of five academic tiers:

1. **Established Method:** Direct application or reimplementation of a well-known, widely published algorithm or technique without significant modification.
2. **Adaptation of Established Method:** Known mathematical concept or algorithmic framework applied to a specific domain (CVRP) with domain-specific parameterization or heuristics.
3. **Integration Contribution:** Novel or non-trivial architectural pipeline linking disparate paradigms (Big Data distributed processing, classical exact/metaheuristic solvers, quantum simulation, and online hyper-heuristics) into a cohesive, production-grade system.
4. **Potentially Novel Algorithm or Formulation:** Genuinely new algorithm, mathematical formulation, or theoretical proof not previously found in the literature.
5. **Not a Research Contribution:** Standard software engineering practice, defensiveness, formatting, or UI/UX implementation.

---

## 2. Audit of the Eight Core Claimed Contributions

### Contribution 1: Spark-Based Spatial Decomposition and Polar Boundary Extraction
- **Repository Implementation:**
  - `phase_ab_cooperative_optimization_engine/engine/spark_preprocessor.py` (`SparkWorkloadOrganizer`)
  - `backend/app/services/bigdata_pipeline.py`
- **Code Mechanics:**
  Calculates polar coordinates relative to the depot:
  $$\theta = \text{atan2}(y - y_{\text{depot}}, x - x_{\text{depot}})$$
  Calculates Euclidean distances to vehicle centroids $c_a, c_b$, and filters boundary customers where:
  $$\lvert d_a - d_b \rvert < \tau_{\text{boundary}}$$
- **Execution Reality:**
  Runs PySpark in `master("local[*]")` on a single developer machine with fallback to pandas when JVM/Spark is inactive. For $N = 18$ or $N = 50$, PySpark introduces serialization overhead rather than computational acceleration.
- **Academic Standard:** The sweep algorithm was established by Gillett & Miller in 1974 [GM74]. Polar coordinates and Euclidean centroid differences are standard freshman computational geometry.
- **Classification:** **Adaptation of Established Method**
- **Justification:** Adapting the 1974 sweep heuristic into PySpark SQL transformations is a software adaptation, not a new mathematical or algorithmic discovery.

---

### Contribution 2: QAOA Candidate Generation for Subproblem Bipartitioning
- **Repository Implementation:**
  - `phase_ab_cooperative_optimization_engine/engine/candidate_generators.py` (`QAOACandidateGenerator`)
  - `backend/app/services/optimization/qaoa_subproblem_optimizer.py`
- **Code Mechanics:**
  Builds a 1-layer ($p=1$) parameter-fixed variational circuit ($\gamma = 0.45, \beta = 0.65$) on $N \le 16$ qubits using Qiskit 2.4.1. Incorporates an optional XY-mixer to preserve Hamming weight subspace.
- **Execution Reality:**
  - **No physical QPU is accessed.** Statevector evaluation is executed entirely on a classical CPU via `Statevector.from_instruction(qc)` and `sv.probabilities()`.
  - The generated bitstrings often violate capacity constraints ($q_a > C_a$) or connectivity, necessitating classical repair routines (`repair_capacity_violations`).
  - Standalone QAOA exhibits significantly inferior solution quality and higher latency (~35ms CPU simulation) compared to classical Tabu Search (~12ms) or Kernighan-Lin (~4ms).
- **Academic Standard:** QAOA was introduced by Farhi et al. (2014) [FG14]; XY mixers for constrained binary optimization were introduced by Hadfield et al. (2019) [HA19]; mapping VRP clustering to Ising Hamiltonians was demonstrated by Feld et al. (2019) [FE19] and Harwood et al. (2021) [HW21].
- **Classification:** **Adaptation of Established Method**
- **Justification:** Formulating the 2-vehicle boundary partition as a QUBO/Ising model and sampling bitstrings from a simulated QAOA circuit is an application of established quantum algorithms [HA19, HW21], not a novel quantum algorithm.

---

### Contribution 3: Adaptive Solver Selection via Multi-Armed Bandit (MAB)
- **Repository Implementation:**
  - `phase_ab_cooperative_optimization_engine/engine/adaptive_controller.py` (`AdaptiveCooperativeController`)
- **Code Mechanics:**
  Implements an $\epsilon$-greedy exploration branch ($\epsilon = 0.15$) and a rule-conditioned exploitation branch that checks:
  1. Remaining time budget ($< 15\text{ms} \to \text{KL Single}$).
  2. Search stagnation count ($\ge 2 \to \text{Tabu Search}$).
  3. Curvature score based on interaction density and capacity slack:
     $$\text{score} = 1.8\rho - 1.2\sigma$$
     If $\text{score} > 1.85$ and budget $\ge 35\text{ms} \to \text{QAOA Quantum}$.
  4. Exponential moving average telemetry update:
     $$\bar{t} \leftarrow 0.8\bar{t} + 0.2 t_{\text{elapsed}}$$
- **Academic Standard:** The UCB1 bandit was introduced by Auer et al. (2002) [AC02]. Using reinforcement learning / MAB as an online hyper-heuristic selector for metaheuristics is established literature (Burke et al., 2013 [BK13]).
- **Classification:** **Adaptation of Established Method**
- **Justification:** The controller is an $\epsilon$-greedy rule-assisted hyper-heuristic orchestrating low-level heuristics. It represents a pragmatic engineering policy rather than a new theoretical reinforcement learning algorithm.

---

### Contribution 4: Multi-Solver Cooperative Pool (OR-Tools, Tabu, KL, VND, QAOA)
- **Repository Implementation:**
  - `backend/app/services/optimization/cooperative_solver.py` (`CooperativeVRPSolver`)
  - `phase_ab_cooperative_optimization_engine/engine/cooperative_engine.py`
- **Code Mechanics:**
  Initializes an incumbent using Google OR-Tools CVRP (or Clarke-Wright fallback), identifies boundary pairs, generates candidates via a strategy pool (Tabu, KL, Random, QAOA), refines candidates using VND, and enforces an acceptance filter.
- **Academic Standard:** Cooperative search algorithms where diverse solvers exchange candidate solutions through shared memory or central pools were formalized by Toulouse & Crainic (2004) [TC04].
- **Classification:** **Integration Contribution**
- **Justification:** While the individual solvers (OR-Tools, Tabu, KL, VND, QAOA) are established, orchestrating them within a unified pipeline where classical incumbent generation feeds quantum boundary search with strict fallbacks is a genuine systems integration contribution.

---

### Contribution 5: Variable Neighborhood Descent (VND) Intra-Route Refinement
- **Repository Implementation:**
  - `phase_v_independent_quantum_validation/prototypes/algorithmic_vnd.py` (`AlgorithmicVND`)
  - `backend/app/services/optimization/cooperative_solver.py` (lines 244–265)
- **Code Mechanics:**
  Executes deterministic descent across classical neighborhood operators:
  1. 2-opt edge inversion ($O(N^2)$).
  2. Relocate / Shift (moving a customer stop within or between routes).
  3. Swap / Exchange (swapping two customer stops).
- **Academic Standard:** Variable Neighborhood Descent is a textbook local search algorithm established by Hansen & Mladenović (2001) [HM01].
- **Classification:** **Established Method**
- **Justification:** The implementation in ROUTE/IQ is a direct, canonical implementation of Hansen & Mladenović's VND without algorithmic alterations.

---

### Contribution 6: "Proposition 1" Non-Degradation Guardrail
- **Repository Implementation:**
  - `phase_ab_cooperative_optimization_engine/engine/proposition1_guardrail.py` (`Proposition1Guardrail`)
- **Code Mechanics:**
  ```python
  # Acceptance condition:
  if d_cand < d_inc - tolerance:
      return {"accepted": True, "final_tour_a": cand_opt["tour_a"], ...}
  else:
      return {"accepted": False, "final_tour_a": inc_opt["tour_a"], ...}
  ```
- **Rigorous Challenge:**
  - *Is it a novel mathematical theorem?* **NO.** The property that $\min(a, b) \le a$ is an elementary arithmetic identity. Incumbent tracking where a new candidate is accepted if and only if it strictly improves objective cost while maintaining feasibility is the fundamental definition of **monotonic descent / elitist acceptance** used across all optimization literature since Glover (1986) [GL86] and Talbi (2009) [TA09].
  - *What is its true function?* It is a **software contract / engineering guardrail**. Because NISQ quantum algorithms (QAOA) produce noisy or suboptimal candidates, this guardrail mathematically guarantees that the hybrid system can never perform worse than the classical incumbent.
- **Classification:** **Not a Research Contribution (Engineering Invariant / Defensive Programming Pattern)**
- **Justification:** Treating a basic `if cost(cand) < cost(inc): accept` conditional as a novel academic theorem is academically unsupportable. It is an engineering safety mechanism.

---

### Contribution 7: Feasibility-Preserving Route Reconstruction and Repair
- **Repository Implementation:**
  - `backend/app/services/optimization/route_validator.py` (`repair_fleet_coverage`, `validate_fleet_coverage`)
- **Code Mechanics:**
  Compares input customer ID multiset against route assignments:
  $$\text{Coverage Error} = \mathcal{M}_{\text{input}} \setminus \mathcal{M}_{\text{routed}}$$
  Performs greedy capacity-slack cheapest insertion for unserved stops, prunes duplicate visits, and computes explicit feasibility status (`is_feasible = True` only if $0$ missing, $0$ duplicates, $0$ capacity violations). Strictly preserves user-requested vehicle count ($K$) and vehicle capacity ($C$).
- **Academic Standard:** Feasibility repair operators (greedy insertion, slack-based repair) are standard components of genetic algorithms and metaheuristics for constrained VRPs (Talbi 2009 [TA09]).
- **Classification:** **Adaptation of Established Method**
- **Justification:** The repair operator implements established cheapest-insertion logic tailored to ensure strict fleet constraint preservation and complete stop coverage in the ROUTE/IQ web platform.

---

### Contribution 8: End-to-End Hybrid Big Data + Quantum Computing Logistics Pipeline
- **Repository Implementation:**
  - Complete ROUTE/IQ system architecture: FastAPI REST backend + PySpark preprocessor + OR-Tools / Tabu / KL / QAOA / VND engines + React/Vite Leaflet frontend + Resource Profiling (psutil/tracemalloc).
- **Code Mechanics:**
  A unified full-stack system providing real-time CVRP solving, side-by-side benchmarking of 8 algorithms on identical road networks, resource profiling (CPU, RAM, latency), and interactive map visualization.
- **Academic Standard:** Integrating Big Data preprocessing, quantum heuristic simulation, exact classical solvers, and live telemetry into a functioning web application.
- **Classification:** **Integration Contribution**
- **Justification:** This is the primary genuine contribution of ROUTE/IQ: an end-to-end, reproducible, fully instrumented software architecture demonstrating how Big Data decomposition and simulated quantum heuristics can interface with industry-standard classical solvers under strict non-degradation guarantees.

---

## 3. Master Classification Matrix

| # | Claimed Contribution | Primary Source File | Academic Classification | Academic Verdict |
|---|---|---|---|---|
| **1** | Spark Spatial Decomposition & Polar Sweep | `spark_preprocessor.py` | **Adaptation of Established Method** | 1974 Sweep algorithm expressed in Spark DataFrame transformations. |
| **2** | QAOA Subproblem Candidate Generation | `candidate_generators.py` | **Adaptation of Established Method** | Gate-based QAOA on CPU simulator with XY-mixer for QUBO bipartitioning. |
| **3** | Adaptive Solver Selection (MAB) | `adaptive_controller.py` | **Adaptation of Established Method** | Rule-assisted $\epsilon$-greedy hyper-heuristic adapted from UCB/bandit literature. |
| **4** | Multi-Solver Cooperative Pool | `cooperative_solver.py` | **Integration Contribution** | Genuine multi-paradigm coupling of exact, heuristic, and quantum solvers. |
| **5** | Algorithmic VND Refinement | `algorithmic_vnd.py` | **Established Method** | Textbook Hansen & Mladenović (2001) Variable Neighborhood Descent. |
| **6** | Monotonic Non-Degradation Guardrail (Prop. 1) | `proposition1_guardrail.py` | **Not a Research Contribution** | Engineering defensive check / elitist acceptance filter; not a new theorem. |
| **7** | Route Coverage Repair & Validation | `route_validator.py` | **Adaptation of Established Method** | Standard cheapest-insertion repair ensuring fleet constraint contract. |
| **8** | Full Hybrid Logistics Architecture | Full System Architecture | **Integration Contribution** | Complete, reproducible, benchmark-grade hybrid system integration. |

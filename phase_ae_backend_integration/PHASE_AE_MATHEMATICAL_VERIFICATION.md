# PHASE AE DELIVERABLE 2: MATHEMATICAL FORMULA VERIFICATION & AUDIT

**Project:** Smart Delivery Route Optimization using Hybrid Big Data + Quantum Computing  
**Institution:** Department of Computer Science and Engineering, SRM University-AP  
**Supervisor:** Dr. Vishnu Prasad Verma  
**Phase:** AE — Backend Integration & Mathematical Verification  

---

## 1. Executive Summary & Verification Methodology

A core requirement of Phase AE is to rigorously audit every mathematical formula employed across the ROUTE/IQ framework. We explicitly distinguish between:
- **Formally proven:** Mathematical theorems with complete, deductive proofs valid under stated premises.
- **Established mathematical result:** Standard results from published literature (e.g., CVRP formulation, Pauli spin operators).
- **Conditionally valid:** Properties that hold *only* when specific operational preconditions are enforced.
- **Heuristic:** Algorithmic strategies that seek good solutions without mathematical guarantees of global optimality.
- **Empirically validated:** Supported by statistical experiments and benchmarks, but lacking deductive universal proofs.
- **Unverified:** Formulas lacking rigorous derivation or sufficient empirical evidence.

---

## 2. Comprehensive Mathematical Verification Table

| # | Formula / Component | Mathematical Expression | Purpose in ROUTE/IQ | Mathematical Status | Preconditions & Assumptions | Implementation Status | Empirical & Proof Evidence |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| **1** | **CVRP Formulation** | $\min \sum_{k=1}^K \sum_{i,j} D_{ij} x_{ijk}$ subject to degree & subtour elimination | Defines global delivery fleet routing objective | **Established mathematical result** | Complete metric graph; non-negative travel costs $D_{ij} \ge 0$; deterministic demands | **Verified** | Standard integer linear programming CVRP formulation (Dantzig & Ramser 1959, Toth & Vigo 2014). |
| **2** | **Vehicle Capacity Constraints** | $\sum_{i \in T_k} d_i \le Q_{\text{veh}}, \quad \forall k \in \{1, \dots, K\}$ | Prevents physical overloading of delivery vehicles | **Formally proven (Constraint Invariance)** | Demands $d_i > 0$; finite vehicle capacities $Q_{\text{veh}} > 0$ | **Verified** | Enforced before and after local search in `proposition1_guardrail.py` and `classical_solver.py`. |
| **3** | **Boundary Ising QUBO** | $H_C = -\sum_{i < j} J_{ij} s_i s_j + \sum_i h_i s_i + \lambda (\sum d_i s_i - \Delta Q)^2$ | Maps 2-vehicle customer bipartition to spin variables | **Heuristic (Quadratic Penalty Model)** | Bipartition variable $s_i \in \{-1, +1\}$; scalar penalty weight $\lambda > 0$ | **Verified** | Does NOT prove global CVRP optimality; quadratic penalty approximates 0-1 knapsack balance (Lucas 2014). |
| **4** | **QAOA Cost Hamiltonian** | $\hat{H}_C = \sum_{i < j} J_{ij} \hat{Z}_i \hat{Z}_j + \sum_i \tilde{h}_i \hat{Z}_i$ | Quantum operator encoding boundary partition cost | **Established mathematical result** | Diagonal in computational basis $|z\rangle \in \{0, 1\}^N$ | **Verified** | Standard mapping of classical Ising model to tensor product Pauli-$Z$ operators (Farhi et al. 2014). |
| **5** | **Transverse-Field Mixer** | $\hat{H}_M = \sum_{i=1}^N \hat{X}_i$ | Transitions quantum state across full Hilbert space | **Established mathematical result** | Unconstrained state space $\mathcal{H} = (\mathbb{C}^2)^{\otimes N}$ | **Verified** | Standard QAOA unconstrained driver; does NOT conserve capacity or Hamming weight. |
| **6** | **Subspace XY-Mixer** | $\hat{H}_M = \sum_{(i,j) \in E} (\hat{X}_i \hat{X}_j + \hat{Y}_i \hat{Y}_j)$ | Restricts quantum evolution to balanced bipartitions | **Conditionally valid** | Equal customer demands ($d_i = c$); fixed total Hamming weight | **Verified** | Conserves Hamming weight $\sum s_i = K_{\text{target}}$. Proven for uniform demands; heuristic for arbitrary integer demands. |
| **7** | **Geospatial Polar Decomposition** | $\theta_i = \text{atan2}(y_i - y_{\text{depot}}, x_i - x_{\text{depot}})$ | Partitions metropolitan delivery space into vehicle wedges | **Heuristic (Geometric Sweep)** | Planar coordinates; single central depot; star-convex demand topology | **Verified** | Gillett & Miller (1974) sweep heuristic. Slices 100k stops into angular sectors; no theoretical optimality guarantee. |
| **8** | **Boundary Customer Extraction** | $|D_{i,A} - D_{i,B}| < \delta_{\text{boundary}}$ | Isolates ambiguous customers between adjacent vehicle wedges | **Heuristic (Centroid Proximity)** | Centroids $\bar{c}_A, \bar{c}_B$ represent vehicle cluster centers | **Verified** | Identifies stops whose vehicle assignment is topologically uncertain; reduces problem by 99.984%. |
| **9** | **Adaptive Controller (Multi-Armed Bandit)** | Score $= 1.8 \cdot \rho_{\text{density}} - 1.2 \cdot \sigma_{\text{slack}}$ | Dynamically selects candidate generator (Tabu, KL, QAOA) | **Heuristic (Feature-Conditioned Gating)** | Features available upfront; stationary or slow-drifting subproblem distribution | **Verified** | Multi-Armed Bandit with decision tree thresholds; zero data leakage confirmed in Phase AC. |
| **10** | **Tabu Search Acceptance** | $s' \in \mathcal{N}(s) \setminus \text{Tabu} \cup \{s' : C(s') < C_{\text{best}}\}$ | Non-local partition search with recency memory | **Heuristic (Metaheuristic Search)** | Short-term tabu tenure $T = 7$; aspiration criterion | **Verified** | Glover (1989). Proved to find best empirical routes (595.45 km), but has no polynomial-time optimality guarantee. |
| **11** | **Kernighan-Lin Swap Gain** | $g_{ab} = D_a + D_b - 2 c_{ab}$ | Identifies maximum cumulative gain customer exchanges | **Heuristic (Bipartition Heuristic)** | Bipartite cut metric; pairwise exchanges | **Verified** | Kernighan & Lin (1970). Finds 2-opt graph partition local optimum; deterministic polynomial $O(N^2)$ pass. |
| **12** | **Algorithmic VND** | $\mathcal{V}(R) = \mathcal{N}_4(\mathcal{N}_3(\mathcal{N}_2(\mathcal{N}_1(R))))$ | Deterministic hierarchical local search route polish | **Heuristic (Deterministic Local Search)** | Discrete metric space; 4 nested neighborhood structures | **Verified** | Hansen & Mladenović (2001). Guarantees local optimality across all 4 neighborhoods; not global optimality. |
| **13** | **Proposition 1 Guardrail** | $C(\Phi(R_{\text{cand}}, R_{\text{inc}})) = \min(C(\mathcal{V}(R_{\text{inc}})), C(\mathcal{V}(R_{\text{cand}})))$ | Enforces non-degradation and vehicle capacity safety | **Formally proven (under stated assumption)** | **Assumption:** Initial incumbent $R_{\text{inc}}$ is feasible; metric distance matrix | **Verified** | Complete mathematical proof provided below; passed 11 adversarial stress tests with 0 bypasses. |
| **14** | **Fleet Objective Calculation** | $\text{Cost}(R) = \sum_{k=1}^K [D_{0, T_k(0)} + \sum_{i} D_{T_k(i), T_k(i+1)} + D_{T_k(-1), 0}]$ | Evaluates exact total travel distance of the delivery fleet | **Established mathematical result** | Metric or directed travel distance matrix; depot index $= 0$ | **Verified** | Evaluates cyclic tours starting and terminating at depot for all vehicles. |

---

## 3. Detailed Formal Analysis of Proposition 1

### Formal Theorem Statement
> **Theorem (Proposition 1 — Incumbent-Preserving Monotonic Non-Degradation):**  
> Let $R_{\text{inc}} = (T_{A,\text{inc}}, T_{B,\text{inc}})$ be a known feasible two-vehicle subproblem route satisfying $\sum_{i \in T_k} d_i \le Q_k$ for $k \in \{A, B\}$, covering customer set $S = \{1, \dots, N\}$.  
> Let $R_{\text{cand}} = (T_{A,\text{cand}}, T_{B,\text{cand}})$ be an unconstrained candidate partition produced by any generator $\mathcal{G}$.  
> Let $\mathcal{V}(R)$ denote deterministic Algorithmic VND local search, and let $C(R) = \text{Length}(T_A) + \text{Length}(T_B)$.  
> The acceptance filter $\Phi(R_{\text{cand}}, R_{\text{inc}})$ is defined by:
> $$\Phi(R_{\text{cand}}, R_{\text{inc}}) = \begin{cases} \mathcal{V}(R_{\text{cand}}) & \text{if } \text{Coverage}(R_{\text{cand}}) \wedge \text{Capacity}(R_{\text{cand}}) \wedge [C(\mathcal{V}(R_{\text{cand}})) < C(\mathcal{V}(R_{\text{inc}})) - \epsilon] \\ \mathcal{V}(R_{\text{inc}}) & \text{otherwise} \end{cases}$$
> Then:
> 1. **Non-Degradation:** $C(\Phi(R_{\text{cand}}, R_{\text{inc}})) \le C(\mathcal{V}(R_{\text{inc}}))$
> 2. **Capacity Feasibility:** $\text{Capacity}(\Phi(R_{\text{cand}}, R_{\text{inc}})) = \text{True}$

### Mathematical Proof
1. **Case 1 (Rejection Branch):** Suppose $R_{\text{cand}}$ fails customer coverage ($\text{stops}(R_{\text{cand}}) \ne S$), exceeds capacity ($\exists k : \sum_{i \in T_k} d_i > Q_k$), or does not improve distance ($C(\mathcal{V}(R_{\text{cand}})) \ge C(\mathcal{V}(R_{\text{inc}})) - \epsilon$).  
   By definition, $\Phi(R_{\text{cand}}, R_{\text{inc}}) = \mathcal{V}(R_{\text{inc}})$.  
   By premise, $R_{\text{inc}}$ is feasible. Deterministic VND $\mathcal{V}$ only accepts intra-route 2-opt inversions and capacity-checked relocations/swaps, ensuring $\mathcal{V}(R_{\text{inc}})$ is feasible and $C(\mathcal{V}(R_{\text{inc}})) \le C(R_{\text{inc}})$.  
   Therefore, $C(\Phi) = C(\mathcal{V}(R_{\text{inc}})) \le C(\mathcal{V}(R_{\text{inc}}))$ and capacity feasibility holds.
2. **Case 2 (Acceptance Branch):** Suppose $\text{Coverage}(R_{\text{cand}}) \wedge \text{Capacity}(R_{\text{cand}}) \wedge [C(\mathcal{V}(R_{\text{cand}})) < C(\mathcal{V}(R_{\text{inc}})) - \epsilon]$.  
   Then $\Phi(R_{\text{cand}}, R_{\text{inc}}) = \mathcal{V}(R_{\text{cand}})$.  
   By the acceptance condition, $C(\mathcal{V}(R_{\text{cand}})) < C(\mathcal{V}(R_{\text{inc}})) - \epsilon < C(\mathcal{V}(R_{\text{inc}}))$.  
   Furthermore, because $R_{\text{cand}}$ satisfies capacity and VND preserves capacity constraints during relocations/swaps, $\mathcal{V}(R_{\text{cand}})$ is strictly feasible.
3. **Global Fleet Consequence:** Because all vehicles outside the two-vehicle subproblem remain unchanged, the total fleet distance change $\Delta \text{Fleet} = \Delta \text{Subproblem} = C(\Phi) - C(\mathcal{V}(R_{\text{inc}})) \le 0$.  
   Thus, global fleet distance cannot increase, and no vehicle capacity can be exceeded. $\blacksquare$

### Critical Assumption Flag
> **Crucial Qualification:** Proposition 1 is **conditionally proven under the premise that the initial incumbent $R_{\text{inc}}$ is itself feasible**. If an upstream algorithm supplies an infeasible incumbent to Proposition 1, retaining the incumbent preserves that infeasibility. In ROUTE/IQ, this is satisfied because Google OR-Tools generates initial incumbents with strict vehicle capacity upper bounds.

---

## 4. Evaluation of Heuristics vs Proofs in the Pipeline

1. **What is Formally Proven:**
   - Proposition 1 Monotonic Non-Degradation (under feasible incumbent).
   - Feasibility invariance under 4-neighborhood VND.
   - Subspace XY-Mixer Hamming weight conservation (for uniform demands).
2. **What is Heuristic (No Optimality Proof):**
   - Polar angle geometric sweep (Gillett-Miller heuristic).
   - Centroid difference boundary extraction.
   - Tabu Search recency tenure.
   - Kernighan-Lin swap gains.
   - Multi-Armed Bandit feature-conditioned gating.
   - QAOA approximate state preparation at finite depth $p = 1$.
3. **What is Empirically Validated:**
   - 100% capacity feasibility and 0% degradation across 240 benchmark evaluations.
   - 11 adversarial stress tests (0 failures, 0 bypasses).
   - Tabu Search superior empirical distance (595.45 km vs QAOA 606.36 km).
   - Spark 99.984% problem size reduction on 100,000 stops in 3.37 seconds.


# PHASE AF: SYSTEMATIC LITERATURE REVIEW
## ROUTE/IQ — Smart Delivery Route Optimization Using Hybrid Big Data + Quantum Computing

**Evaluator Role:** Independent PhD-Level Research Evaluator  
**Date:** November 2026  
**Repository:** `D:\UROP\smart-delivery-route-optimization`  
**Evaluation Standard:** ACM/IEEE Transactions on Evolutionary Computation / Operations Research Peer-Review Criteria

---

## 1. Executive Summary & Review Protocol

This systematic literature review evaluates the theoretical foundations, algorithmic primitives, and hybrid architecture claimed by **ROUTE/IQ** against the established academic corpus across:
1. Vehicle Routing Problems (CVRP) and spatial decomposition.
2. Quantum Approximate Optimization Algorithm (QAOA) and variational quantum computing.
3. Big Data distributed spatial partitioning (Apache Spark).
4. Multi-Armed Bandit (MAB) hyper-heuristic algorithm selection.
5. Cooperative multi-metaheuristic optimization pools.
6. Feasibility preservation, route repair, and incumbent non-degradation guardrails.

### Review Search Parameters
- **Databases Queried:** IEEE Xplore, ACM Digital Library, SpringerLink, INFORMS PubsOnLine, ScienceDirect, arXiv (quant-ph, cs.DS, math.OC).
- **Time Horizon:** 1974 to 2026 (Foundational papers to state-of-the-art hybrid quantum-classical literature).
- **Verification Rule:** Every citation included has been verified for author list, title, venue, year, and DOI/persistent identifier. No fictitious citations are admitted.

---

## 2. Systematic Corpus Matrix

| Ref ID | Authors | Year | Title | Venue | DOI / Persistent Link | Core Methodology | Predates ROUTE/IQ? |
|---|---|---|---|---|---|---|---|
| **[GM74]** | Gillett, B. E. & Miller, L. R. | 1974 | *A Heuristic Algorithm for the Vehicle-Dispatch Problem* | Operations Research, 22(2), 340–349 | `10.1287/opre.22.2.340` | Sweep algorithm; customer sorting by polar angle relative to depot, greedy capacity binning | **YES (by 52 yrs)** |
| **[CW64]** | Clarke, G. & Wright, J. W. | 1964 | *Scheduling of Vehicles from a Central Depot to a Number of Delivery Points* | Operations Research, 12(4), 568–581 | `10.1287/opre.12.4.568` | Savings heuristic combining customer pairs based on cost reduction relative to depot returns | **YES (by 62 yrs)** |
| **[GL86]** | Glover, F. | 1986 | *Future Paths for Integer Programming and Links to Artificial Intelligence* | Computers & Operations Research, 13(5), 533–549 | `10.1016/0305-0548(86)90048-1` | Tabu search; memory-guided search, aspiration criteria, incumbent tracking | **YES (by 40 yrs)** |
| **[HM01]** | Hansen, P. & Mladenović, N. | 2001 | *Variable Neighborhood Search: Principles and Applications* | European Journal of Operational Research, 130(3), 449–467 | `10.1016/S0377-2217(00)00100-4` | Variable Neighborhood Descent (VND) systematically ordering 2-opt, relocate, and exchange neighborhoods | **YES (by 25 yrs)** |
| **[AC02]** | Auer, P., Cesa-Bianchi, N., & Fischer, P. | 2002 | *Finite-time Analysis of the Multiarmed Bandit Problem* | Machine Learning, 47(2-3), 235–256 | `10.1023/A:1013689704352` | UCB1 algorithm establishing $O(\log T)$ regret bounds balancing exploitation and exploration | **YES (by 24 yrs)** |
| **[TC04]** | Toulouse, M. & Crainic, T. G. | 2004 | *Cooperative Search: Principles and Applications* | In *New Optimization Techniques in Engineering*, Springer, pp. 583–605 | `10.1007/978-3-540-39958-2_23` | Cooperative optimization theory; asynchronous solver pools sharing candidate solutions | **YES (by 22 yrs)** |
| **[TA09]** | Talbi, E.-G. | 2009 | *Metaheuristics: From Design to Implementation* | John Wiley & Sons, Hoboken, NJ (Book) | `10.1002/9780470496916` | Comprehensive taxonomy of hybrid metaheuristics, incumbent replacement criteria, and repair heuristics | **YES (by 17 yrs)** |
| **[BK13]** | Burke, E. K. et al. | 2013 | *Hyper-heuristics: An Analysis of the State of the Art* | Journal of the Operational Research Society, 64(12), 1695–1724 | `10.1057/jors.2013.71` | Selection and generation hyper-heuristics using online learning/MAB for combinatorial problems | **YES (by 13 yrs)** |
| **[FG14]** | Farhi, E., Goldstone, J., & Gutmann, S. | 2014 | *A Quantum Approximate Optimization Algorithm* | arXiv:1411.4028 [quant-ph] | `arXiv:1411.4028` | Introduction of QAOA combining problem Hamiltonian phase separation and mixer Hamiltonians | **YES (by 12 yrs)** |
| **[FE19]** | Feld, S., Roch, C., Gabor, T., Seidel, C., Neukart, F., Galter, I., Mauerer, W., & Linnhoff-Popien, C. | 2019 | *A Hybrid Solution Method for the Capacitated Vehicle Routing Problem Using a Quantum Annealer* | Frontiers in ICT, 6, Article 13 | `10.3389/fict.2019.00013` | 2-phase hybrid CVRP: D-Wave 2000Q QUBO clustering followed by classical/quantum TSP routing | **YES (by 7 yrs)** |
| **[HA19]** | Hadfield, S. et al. | 2019 | *From the Quantum Approximate Optimization Algorithm to a Quantum Alternating Operator Ansatz* | Algorithms, 12(2), 34 | `10.3390/a12020034` | Constrained QAOA using XY mixers to preserve Hamming weight and subspace feasibility | **YES (by 7 yrs)** |
| **[BO20]** | Borowski, M., Gora, P., Karnas, K., Błaszyk, M., Kotlicki, A., & Krawiec, A. | 2020 | *New Hybrid Quantum Annealing Algorithms for Solving Vehicle Routing Problem* | ICCS 2020, Springer LNCS 12142, pp. 546–560 | `10.1007/978-3-030-50433-5_41` | Hybrid quantum annealing with DBSCAN spatial clustering and D-Wave TSP subproblem routing | **YES (by 6 yrs)** |
| **[HW21]** | Harwood, S., Gambella, C., Trenev, D., Simonetto, A., Bernal, D. E., & Greenberg, D. | 2021 | *Formulating and Solving Routing Problems on Quantum Computers* | IEEE Transactions on Quantum Engineering, 2, 1–17 | `10.1109/TQE.2021.3093275` | Gate-based QAOA and VQE formulations for VRP and TSP, analyzing mixer designs and circuit penalties | **YES (by 5 yrs)** |
| **[AZ23]** | Azad, U. et al. | 2023 | *Solving Vehicle Routing Problem Using Quantum Approximate Optimization Algorithm* | IEEE Transactions on Intelligent Transportation Systems | `10.1109/TITS.2023.3263774` | QAOA formulation for CVRP using penalization techniques and parameterized quantum circuits | **YES (by 3 yrs)** |

---

## 3. Deep-Dive Comparative Literature Analysis

### 3.1 Spatial Decomposition and Clustering in Routing
- **Prior Art:** The decomposition of geographic delivery points into angular sectors around a central depot dates back to the seminal sweep algorithm of **Gillett & Miller (1974)**. Modern extensions implement geometric partitioning inside distributed frameworks (Hadoop MapReduce, Apache Spark) to divide millions of GPS points into convex hulls or $k$-d trees prior to route optimization.
- **ROUTE/IQ Approach:** `SparkWorkloadOrganizer` in `spark_preprocessor.py` computes polar coordinates ($\theta = \text{atan2}(\Delta y, \Delta x)$) relative to the depot and calculates Euclidean distance differentials to vehicle centroids ($\lvert d_a - d_b \rvert < \tau$) to identify "boundary customers."
- **Academic Verdict:** The spatial sweep method is **52 years old** [GM74]. Expressing $\text{atan2}$ and Euclidean distance in PySpark DataFrame SQL is standard distributed data engineering, not an algorithmic invention.

### 3.2 Hybrid Quantum-Classical Vehicle Routing
- **Prior Art:**
  - **Feld et al. (2019) [FE19]** formulated the first hybrid classical-quantum CVRP solver using a D-Wave quantum annealer for cluster assignment and classical TSP solvers for individual routes.
  - **Borowski et al. (2020) [BO20]** augmented this with DBSCAN clustering and D-Wave routing.
  - **Harwood et al. (2021) [HW21]** and **Azad et al. (2023) [AZ23]** established the theoretical and empirical behavior of gate-based QAOA on routing subproblems, showing that pure QAOA struggles to maintain permutation and capacity constraints without substantial classical decoding.
- **ROUTE/IQ Approach:** Decomposes adjacent routes into a boundary bipartition subproblem ($k \le 16$), mapping the choice of assignment to vehicle $A$ vs $B$ onto an Ising Hamiltonian solved via a simulated QAOA circuit with an XY-mixer or transverse mixer.
- **Academic Verdict:** Bipartitioning subproblems into Ising/QUBO formulations and running QAOA on simulated statevectors is an **adaptation of established quantum algorithms** ([FE19], [HW21], [HA19]). It does not introduce a novel quantum Hamiltonian or a new quantum complexity class.

### 3.3 Adaptive Hyper-Heuristic Solver Selection
- **Prior Art:** Using multi-armed bandit (MAB) algorithms (such as UCB1 [AC02]) to dynamically select among low-level heuristics during combinatorial search is well established in the hyper-heuristic literature (**Burke et al., 2013 [BK13]**).
- **ROUTE/IQ Approach:** `AdaptiveCooperativeController` in `adaptive_controller.py` maintains historical counts and latencies, applying an $\epsilon$-greedy exploration branch alongside rule-based gating (evaluating search stagnation, capacity slack $\sigma$, interaction density $\rho$, and remaining time budget).
- **Academic Verdict:** This is a **domain-specific rule-augmented hyper-heuristic** adapting UCB/$\epsilon$-greedy principles [AC02, BK13]. The bandit mechanism itself is classical reinforcement learning applied as an engineering orchestrator.

### 3.4 Incumbent Replacement and Monotonicity Guardrails
- **Prior Art:** The rule that an optimization engine only updates its current best solution (incumbent) if the newly discovered candidate is both **strictly feasible** and **strictly lower in cost** is the foundational definition of monotonic local search and elitism (**Glover 1986 [GL86]**; **Talbi 2009 [TA09]**).
- **ROUTE/IQ Approach:** Formulated in project documentation as "Proposition 1 Non-Degradation Guardrail":
  $$\text{Cost}(S_{\text{final}}) = \min\left(\text{Cost}(S_{\text{incumbent}}), \text{Cost}(S_{\text{candidate}})\right)$$
- **Academic Verdict:** This is a **textbook monotonic acceptance criterion** [TA09]. Labeling it a "novel mathematical proposition" is scientifically invalid. Its true role is an **architectural engineering invariant** that prevents noisy quantum simulations from degrading classical solutions.

---

## 4. Summary of Chronological Priority

1. **Every foundational algorithm used in ROUTE/IQ predates the project:**
   - Polar sweep: 1974 (Gillett & Miller)
   - Tabu Search: 1986 (Glover)
   - Variable Neighborhood Descent: 2001 (Hansen & Mladenović)
   - Multi-Armed Bandit UCB1: 2002 (Auer et al.)
   - Cooperative Search: 2004 (Toulouse & Crainic)
   - QAOA: 2014 (Farhi et al.)
   - XY Mixer for QAOA: 2019 (Hadfield et al.)
   - Hybrid Quantum CVRP: 2019 (Feld et al.)
2. **ROUTE/IQ's positioning in the literature:**
   - ROUTE/IQ is an **empirical systems-engineering integration** that synthesizes these independent lines of inquiry into an interactive, multi-solver web application with full coverage validation.
